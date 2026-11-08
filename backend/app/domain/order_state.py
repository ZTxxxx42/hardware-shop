"""订单状态机(架构设计.md 3.3)。

仅允许:待支付→已支付/已取消;已支付→已发货→已完成。MVP 不做退款。
"""
from __future__ import annotations

from enum import StrEnum

from app.core.exceptions import InvalidStateTransitionError


class OrderStatus(StrEnum):
    PENDING_PAYMENT = "PENDING_PAYMENT"  # 待支付
    PAID = "PAID"                        # 已支付
    SHIPPED = "SHIPPED"                  # 已发货
    COMPLETED = "COMPLETED"              # 已完成
    CANCELLED = "CANCELLED"              # 已取消


# 合法流转表
_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.PENDING_PAYMENT: frozenset({OrderStatus.PAID, OrderStatus.CANCELLED}),
    OrderStatus.PAID: frozenset({OrderStatus.SHIPPED}),
    OrderStatus.SHIPPED: frozenset({OrderStatus.COMPLETED}),
    OrderStatus.COMPLETED: frozenset(),
    OrderStatus.CANCELLED: frozenset(),
}


def can_transition(current: OrderStatus | str, target: OrderStatus | str) -> bool:
    return OrderStatus(target) in _TRANSITIONS.get(OrderStatus(current), frozenset())


def assert_transition(current: OrderStatus | str, target: OrderStatus | str) -> None:
    current = OrderStatus(current)
    target = OrderStatus(target)
    if not can_transition(current, target):
        raise InvalidStateTransitionError(f"非法订单状态流转:{current.value} -> {target.value}")


def next_statuses(current: OrderStatus | str) -> frozenset[OrderStatus]:
    return _TRANSITIONS.get(OrderStatus(current), frozenset())
