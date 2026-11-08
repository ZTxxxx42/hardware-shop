"""购物车用例:增删改查与实时计价(价格不落库)。"""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError, NotFoundError
from app.core.security import AuthUser
from app.domain.pricing import resolve_product_price, subtotal
from app.models import CartItem, Product, ProductPrice  # 由 database agent 提供
from app.schemas.cart import CartItemOut, CartSummary
from app.services.common import calculate_freight


def _price_map(db: Session, product_id: int) -> dict[str, Decimal]:
    rows = db.scalars(select(ProductPrice).where(ProductPrice.product_id == product_id)).all()
    return {r.level_code: r.price for r in rows}


def _to_item(db: Session, ci: CartItem, level_code: str | None) -> CartItemOut | None:
    product = db.get(Product, ci.product_id)
    if product is None:
        return None
    price = resolve_product_price(product.retail_price, level_code, _price_map(db, product.id))
    return CartItemOut(
        id=ci.id,
        product_id=product.id,
        name=product.name,
        model=product.model,
        main_image=product.main_image,
        quantity=ci.quantity,
        retail_price=product.retail_price,
        price=price,
        subtotal=subtotal(price, ci.quantity),
    )


def list_cart(db: Session, user: AuthUser) -> CartSummary:
    rows = db.scalars(select(CartItem).where(CartItem.user_id == user.id)).all()
    items = [item for ci in rows if (item := _to_item(db, ci, user.level_code)) is not None]
    product_amount = sum((i.subtotal for i in items), Decimal("0"))
    freight_amount = calculate_freight(product_amount)
    return CartSummary(
        items=items,
        product_amount=product_amount,
        freight_amount=freight_amount,
        total_amount=product_amount + freight_amount,
    )


def add_item(db: Session, user: AuthUser, product_id: int, quantity: int) -> CartSummary:
    product = db.get(Product, product_id)
    if product is None:
        raise NotFoundError("商品不存在")

    existing = db.scalars(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product_id)
    ).first()
    if existing is not None:
        existing.quantity += quantity
    else:
        db.add(CartItem(user_id=user.id, product_id=product_id, quantity=quantity))
    db.commit()
    return list_cart(db, user)


def update_item(db: Session, user: AuthUser, item_id: int, quantity: int) -> CartSummary:
    item = db.get(CartItem, item_id)
    if item is None or item.user_id != user.id:
        raise NotFoundError("购物车项不存在")
    item.quantity = quantity
    db.commit()
    return list_cart(db, user)


def remove_item(db: Session, user: AuthUser, item_id: int) -> CartSummary:
    item = db.get(CartItem, item_id)
    if item is None or item.user_id != user.id:
        raise NotFoundError("购物车项不存在")
    db.delete(item)
    db.commit()
    return list_cart(db, user)
