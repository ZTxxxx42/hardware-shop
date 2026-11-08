"""购物车路由(会员)。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_member
from app.core.security import AuthUser
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartSummary
from app.services import cart as cart_service

router = APIRouter(prefix="/cart", tags=["购物车"], dependencies=[Depends(require_member)])


@router.get("", response_model=CartSummary)
def list_cart(
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> CartSummary:
    return cart_service.list_cart(db, user)


@router.post("/items", response_model=CartSummary)
def add_item(
    payload: CartItemAdd,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> CartSummary:
    return cart_service.add_item(db, user, payload.product_id, payload.quantity)


@router.patch("/items/{item_id}", response_model=CartSummary)
def update_item(
    item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> CartSummary:
    return cart_service.update_item(db, user, item_id, payload.quantity)


@router.delete("/items/{item_id}", response_model=CartSummary)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> CartSummary:
    return cart_service.remove_item(db, user, item_id)
