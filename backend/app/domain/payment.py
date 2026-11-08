"""支付领域规则:渠道/状态枚举与幂等判断。"""
from __future__ import annotations

from enum import StrEnum


class PaymentChannel(StrEnum):
    WECHAT = "wechat"
    ALIPAY = "alipay"


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CLOSED = "CLOSED"


def is_success_payment(status: str | PaymentStatus) -> bool:
    return PaymentStatus(status) == PaymentStatus.SUCCESS
