"""支付用例:回调验签、幂等处理、状态流转。

幂等保证(架构设计.md 6.2):payment(order_id, channel) 唯一约束 + 订单状态机 + 事务。
库存已在下单时预占,回调不二次扣减(见 services/order.py 与 docs/api/issues.md)。
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.domain.order_state import OrderStatus, assert_transition
from app.domain.payment import PaymentStatus, is_success_payment
from app.models import Order, Payment  # 由 database agent 提供
from app.schemas.payment import PaymentNotifyPayload


def _verify_signature(channel: str, payload: PaymentNotifyPayload) -> None:
    """渠道验签桩。接入真实网关后替换为微信 v3 / 支付宝 RSA2 验签。"""
    # TODO: 微信 AEAD_AES_256_GCM / 支付宝 RSA2 验签;验签失败抛 PaymentVerifyError
    return None


def handle_notify(db: Session, channel: str, payload: PaymentNotifyPayload) -> bool:
    """处理支付网关异步回调,返回 True 表示应向网关应答成功。"""
    _verify_signature(channel, payload)

    order = db.scalars(select(Order).where(Order.order_no == payload.order_no)).first()
    if order is None:
        raise NotFoundError("订单不存在")

    payment = db.scalars(
        select(Payment).where(Payment.order_id == order.id, Payment.channel == channel)
    ).first()

    # 幂等命中:同一流水已成功,直接应答,不重复流转
    if payment is not None and is_success_payment(payment.status):
        return True

    now = dt.datetime.now(dt.timezone.utc)

    # 订单已支付但流水未成功(异常中断):补齐流水后幂等应答
    if order.status == OrderStatus.PAID:
        if payment is None:
            db.add(
                Payment(
                    order_id=order.id,
                    channel=channel,
                    trade_no=payload.trade_no,
                    amount=payload.amount,
                    status=PaymentStatus.SUCCESS,
                    paid_at=now,
                )
            )
        else:
            payment.trade_no = payload.trade_no
            payment.amount = payload.amount
            payment.status = PaymentStatus.SUCCESS
            payment.paid_at = now
        db.commit()
        return True

    assert_transition(order.status, OrderStatus.PAID)

    if payment is None:
        payment = Payment(
            order_id=order.id,
            channel=channel,
            trade_no=payload.trade_no,
            amount=payload.amount,
            status=PaymentStatus.SUCCESS,
            paid_at=now,
        )
        db.add(payment)
    else:
        payment.trade_no = payload.trade_no
        payment.amount = payload.amount
        payment.status = PaymentStatus.SUCCESS
        payment.paid_at = now

    order.status = OrderStatus.PAID

    try:
        db.commit()
    except IntegrityError:
        # 并发重复回调:唯一约束(order_id, channel)拦截后,重载幂等应答
        db.rollback()
        payment = db.scalars(
            select(Payment).where(Payment.order_id == order.id, Payment.channel == channel)
        ).first()
        if payment is not None and is_success_payment(payment.status):
            return True
        raise
    return True
