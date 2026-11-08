"""订单路由(会员)。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_member
from app.core.security import AuthUser
from app.schemas.order import OrderBrief, OrderCreate, OrderDetail
from app.services import order as order_service

router = APIRouter(prefix="/orders", tags=["订单"], dependencies=[Depends(require_member)])


@router.post("", response_model=OrderDetail, status_code=201)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> OrderDetail:
    return order_service.create_order(db, user, payload)


@router.get("", response_model=list[OrderBrief])
def list_orders(
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> list[OrderBrief]:
    return order_service.list_orders(db, user)


@router.get("/{order_id}", response_model=OrderDetail)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> OrderDetail:
    return order_service.get_order(db, user, order_id)


@router.post("/{order_id}/cancel", response_model=OrderDetail)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> OrderDetail:
    return order_service.cancel_order(db, user, order_id)


@router.post("/{order_id}/confirm", response_model=OrderDetail)
def confirm_receipt(
    order_id: int,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> OrderDetail:
    return order_service.confirm_receipt(db, user, order_id)
