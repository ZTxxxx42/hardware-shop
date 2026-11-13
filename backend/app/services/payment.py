"""支付用例:回调验签、幂等处理、状态流转。

幂等保证(架构设计.md 6.2):payment(order_id, channel) 唯一约束 + 订单状态机 + 事务。
库存已在下单时预占,回调不二次扣减(见 services/order.py 与 docs/api/issues.md)。
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, PaymentVerifyError
from app.domain.order_state import OrderStatus, assert_transition
from app.domain.payment import PaymentStatus, is_success_payment
from app.models import Order, Payment  # 由 database agent 提供
from app.schemas.payment import PaymentNotifyPayload


def _verify_signature(channel: str, payload: PaymentNotifyPayload) -> None:
    """未接入真实渠道验签前必须失败关闭，不得流转订单。"""
    raise PaymentVerifyError(
        "支付渠道真实验签尚未实现，拒绝处理回调",
        status_code=503,
    )


def handle_notify(db: Session, channel: str, payload: PaymentNotifyPayload) -> bool:
    """处理支付网关异步回调,返回 True 表示应向网关应答成功。"""
    _verify_signature(channel, payload)

    if channel != payload.channel:
        raise PaymentVerifyError("支付渠道与回调载荷不一致")
    if payload.status != PaymentStatus.SUCCESS:
        raise PaymentVerifyError("仅接受支付成功状态的回调")

    order = db.scalars(
        select(Order).where(Order.order_no == payload.order_no).with_for_update()
    ).first()
    if order is None:
        raise NotFoundError("订单不存在")
    if payload.amount != order.total_amount:
        raise PaymentVerifyError("支付金额与订单金额不一致")

    payment = db.scalars(
        select(Payment).where(Payment.order_id == order.id, Payment.channel == channel)
    ).first()
    if payment is not None and payload.amount != payment.amount:
        raise PaymentVerifyError("支付金额与已有支付单不一致")

    # 幂等命中必须同时核对流水号，禁止不同流水复用成功状态。
    if payment is not None and is_success_payment(payment.status):
        if payment.trade_no != payload.trade_no:
            raise PaymentVerifyError("重复支付回调的交易流水号不一致")
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
        # 并发重复回调:唯一约束(order_id, channel)拦截后,重载并完整核对幂等条件
        db.rollback()
        payment = db.scalars(
            select(Payment).where(Payment.order_id == order.id, Payment.channel == channel)
        ).first()
        if payment is not None and is_success_payment(payment.status):
            if payment.trade_no != payload.trade_no or payment.amount != payload.amount:
                raise PaymentVerifyError("并发重复支付回调的数据不一致")
            return True
        raise
    return True
