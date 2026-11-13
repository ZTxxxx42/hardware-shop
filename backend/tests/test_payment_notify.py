from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.core.exceptions import PaymentVerifyError
from app.domain.order_state import OrderStatus
from app.domain.payment import PaymentStatus
from app.models import Order, Payment
from app.schemas.payment import PaymentNotifyPayload
from app.services import payment as payment_service


def make_payload(**overrides: object) -> PaymentNotifyPayload:
    values: dict[str, object] = {
        "order_no": "SO-TEST-1",
        "channel": "wechat",
        "trade_no": "trade-1",
        "amount": Decimal("10.00"),
        "status": "SUCCESS",
    }
    values.update(overrides)
    return PaymentNotifyPayload.model_validate(values)


def create_pending_order(db: Session, payment_amount: Decimal = Decimal("10.00")) -> Order:
    order = Order(
        id=1,
        order_no="SO-TEST-1",
        user_id=1,
        status=OrderStatus.PENDING_PAYMENT,
        product_amount=Decimal("10.00"),
        freight_amount=Decimal("0.00"),
        total_amount=Decimal("10.00"),
        receiver_name="测试收货人",
        receiver_phone="13800000000",
        receiver_region="测试地区",
        receiver_detail="测试地址",
    )
    db.add(order)
    db.add(
        Payment(
            id=1,
            order_id=order.id,
            channel="wechat",
            trade_no=None,
            amount=payment_amount,
            status=PaymentStatus.PENDING,
        )
    )
    db.commit()
    return order


def bypass_signature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(payment_service, "_verify_signature", lambda channel, payload: None)


def test_unimplemented_channel_verification_fails_closed() -> None:
    with pytest.raises(PaymentVerifyError) as exc_info:
        payment_service.handle_notify(None, "wechat", make_payload())  # type: ignore[arg-type]
    assert exc_info.value.status_code == 503


def test_non_success_payload_is_rejected(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    order = create_pending_order(db)
    bypass_signature(monkeypatch)
    with pytest.raises(PaymentVerifyError):
        payment_service.handle_notify(db, "wechat", make_payload(status="FAILED"))
    assert order.status == OrderStatus.PENDING_PAYMENT


def test_amount_must_match_order(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    order = create_pending_order(db)
    bypass_signature(monkeypatch)
    with pytest.raises(PaymentVerifyError, match="订单金额"):
        payment_service.handle_notify(db, "wechat", make_payload(amount=Decimal("9.99")))
    assert order.status == OrderStatus.PENDING_PAYMENT


def test_amount_must_match_existing_payment(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    create_pending_order(db, payment_amount=Decimal("9.99"))
    bypass_signature(monkeypatch)
    with pytest.raises(PaymentVerifyError, match="已有支付单"):
        payment_service.handle_notify(db, "wechat", make_payload())


def test_duplicate_success_must_reuse_trade_no(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    order = create_pending_order(db)
    order.status = OrderStatus.PAID
    payment = db.get(Payment, 1)
    assert payment is not None
    payment.status = PaymentStatus.SUCCESS
    payment.trade_no = "trade-1"
    db.commit()
    bypass_signature(monkeypatch)

    assert payment_service.handle_notify(db, "wechat", make_payload()) is True
    with pytest.raises(PaymentVerifyError, match="流水号"):
        payment_service.handle_notify(db, "wechat", make_payload(trade_no="trade-2"))
