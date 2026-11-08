"""支付 schema。"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PaymentOut(ORMModel):
    id: int
    order_id: int
    channel: str
    trade_no: str | None = None
    amount: Decimal
    status: str
    paid_at: datetime | None = None


class PaymentNotifyPayload(BaseModel):
    """支付网关异步回调载荷。字段随渠道略有差异,联调时按渠道适配。"""

    order_no: str
    channel: str
    trade_no: str
    amount: Decimal = Field(ge=0)
    status: str = "SUCCESS"
    sign: str | None = None
    extra: dict = Field(default_factory=dict)
