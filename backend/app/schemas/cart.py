"""购物车 schema。价格不落库,展示时按登录态实时计算。"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemOut(BaseModel):
    id: int
    product_id: int
    name: str
    model: str | None = None
    main_image: str | None = None
    quantity: int
    retail_price: Decimal
    price: Decimal
    subtotal: Decimal


class CartSummary(BaseModel):
    items: list[CartItemOut]
    product_amount: Decimal
    freight_amount: Decimal
    total_amount: Decimal
