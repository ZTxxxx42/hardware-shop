"""订单 schema。订单项保留名称/单价快照。"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.domain.payment import PaymentChannel
from app.schemas.payment import PaymentOut


class OrderCreate(BaseModel):
    address_id: int
    channel: PaymentChannel = PaymentChannel.WECHAT
    remark: str | None = None


class OrderItemOut(BaseModel):
    id: int
    product_id: int | None = None
    product_name: str
    price: Decimal
    quantity: int
    subtotal: Decimal


class OrderBrief(BaseModel):
    id: int
    order_no: str
    status: str
    product_amount: Decimal
    freight_amount: Decimal
    total_amount: Decimal
    created_at: datetime


class OrderDetail(OrderBrief):
    items: list[OrderItemOut] = Field(default_factory=list)
    address_snapshot: dict[str, Any] | None = None
    payments: list[PaymentOut] = Field(default_factory=list)
