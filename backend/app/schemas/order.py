"""订单 schema。订单项保留名称/单价快照。"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, Field, StringConstraints

from app.domain.payment import PaymentChannel
from app.schemas.payment import PaymentOut


class OrderCreate(BaseModel):
    address_id: int
    channel: PaymentChannel = PaymentChannel.WECHAT
    remark: str | None = Field(default=None, max_length=500)


class OrderShipRequest(BaseModel):
    carrier: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=64),
    ]
    tracking_no: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=64),
    ]


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
    remark: str | None = None
    carrier: str | None = None
    tracking_no: str | None = None
    shipped_at: datetime | None = None
    created_at: datetime


class OrderDetail(OrderBrief):
    items: list[OrderItemOut] = Field(default_factory=list)
    address_snapshot: dict[str, Any] | None = None
    payments: list[PaymentOut] = Field(default_factory=list)
