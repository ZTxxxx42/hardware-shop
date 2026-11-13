"""订单用例:下单 = 校验库存 + 按等级锁价 + 创建订单 + 创建支付单。

库存占用策略(详见 docs/api/issues.md):下单预占扣减库存,取消回补;
支付回调仅做幂等状态流转,不二次扣减,避免「已付款无库存」边界。
"""
from __future__ import annotations

import datetime as dt
import random
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError, NotFoundError
from app.core.security import AuthUser
from app.domain.inventory import assert_stock_sufficient, deduct_stock, restore_stock
from app.domain.order_state import OrderStatus, assert_transition
from app.domain.payment import PaymentStatus
from app.domain.pricing import resolve_product_price, subtotal
from app.models import (  # 由 database agent 提供
    Address,
    CartItem,
    Order,
    OrderItem,
    Payment,
    Product,
    ProductPrice,
)
from app.schemas.order import (
    OrderBrief,
    OrderCreate,
    OrderDetail,
    OrderItemOut,
    OrderShipRequest,
)
from app.schemas.payment import PaymentOut
from app.services.common import calculate_freight


def _gen_order_no() -> str:
    return f"SO{dt.datetime.now().strftime('%Y%m%d%H%M%S%f')}{random.randint(1000, 9999)}"


def _price_map(db: Session, product_id: int) -> dict[str, Decimal]:
    rows = db.scalars(select(ProductPrice).where(ProductPrice.product_id == product_id)).all()
    return {r.level_code: r.price for r in rows}


def _address_snapshot(order: Order) -> dict[str, str]:
    """从订单展开列拼装响应用地址快照(与 database agent 的 order 列对齐)。"""
    return {
        "receiver": order.receiver_name,
        "phone": order.receiver_phone,
        "region": order.receiver_region,
        "detail": order.receiver_detail,
    }


def _order_detail(db: Session, order: Order) -> OrderDetail:
    items = [
        OrderItemOut(
            id=i.id,
            product_id=i.product_id,
            product_name=i.product_name,
            price=i.price,
            quantity=i.quantity,
            subtotal=i.subtotal,
        )
        for i in order.items
    ]
    payments = [PaymentOut.model_validate(p) for p in order.payments]
    return OrderDetail(
        id=order.id,
        order_no=order.order_no,
        status=order.status,
        product_amount=order.product_amount,
        freight_amount=order.freight_amount,
        total_amount=order.total_amount,
        remark=order.remark,
        carrier=order.carrier,
        tracking_no=order.tracking_no,
        shipped_at=order.shipped_at,
        created_at=order.created_at,
        items=items,
        address_snapshot=_address_snapshot(order),
        payments=payments,
    )


def create_order(db: Session, user: AuthUser, payload: OrderCreate) -> OrderDetail:
    address = db.get(Address, payload.address_id)
    if address is None or address.user_id != user.id:
        raise BusinessError("收货地址不存在")

    cart_items = db.scalars(select(CartItem).where(CartItem.user_id == user.id)).all()
    if not cart_items:
        raise BusinessError("购物车为空,无法下单")

    product_amount = Decimal("0")
    prepared: list[tuple[Product, Decimal, int, Decimal]] = []
    for ci in cart_items:
        product = db.get(Product, ci.product_id)
        if product is None:
            raise BusinessError("购物车中存在已下架商品")
        # 预占前先校验库存
        assert_stock_sufficient(product.stock, ci.quantity)
        price = resolve_product_price(product.retail_price, user.level_code, _price_map(db, product.id))
        sub = subtotal(price, ci.quantity)
        product_amount += sub
        prepared.append((product, price, ci.quantity, sub))

    freight_amount = calculate_freight(product_amount)
    total_amount = product_amount + freight_amount

    order = Order(
        user_id=user.id,
        order_no=_gen_order_no(),
        status=OrderStatus.PENDING_PAYMENT,
        product_amount=product_amount,
        freight_amount=freight_amount,
        total_amount=total_amount,
        receiver_name=address.receiver,
        receiver_phone=address.phone,
        receiver_region=address.region,
        receiver_detail=address.detail,
        remark=payload.remark,
        created_at=dt.datetime.now(dt.timezone.utc),
    )
    db.add(order)
    db.flush()

    for product, price, quantity, sub in prepared:
        product.stock = deduct_stock(product.stock, quantity)  # 预占扣减
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                price=price,
                quantity=quantity,
                subtotal=sub,
            )
        )

    db.add(
        Payment(
            order_id=order.id,
            channel=payload.channel,
            amount=total_amount,
            status=PaymentStatus.PENDING,
        )
    )

    for ci in cart_items:
        db.delete(ci)

    db.commit()
    db.refresh(order)
    return _order_detail(db, order)


def list_orders(db: Session, user: AuthUser) -> list[OrderBrief]:
    rows = db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.id.desc())).all()
    return [
        OrderBrief(
            id=o.id,
            order_no=o.order_no,
            status=o.status,
            product_amount=o.product_amount,
            freight_amount=o.freight_amount,
            total_amount=o.total_amount,
            remark=o.remark,
            carrier=o.carrier,
            tracking_no=o.tracking_no,
            shipped_at=o.shipped_at,
            created_at=o.created_at,
        )
        for o in rows
    ]


def get_order(db: Session, user: AuthUser, order_id: int) -> OrderDetail:
    order = db.get(Order, order_id)
    if order is None or order.user_id != user.id:
        raise NotFoundError("订单不存在")
    return _order_detail(db, order)


def cancel_order(db: Session, user: AuthUser, order_id: int) -> OrderDetail:
    order = db.get(Order, order_id)
    if order is None or order.user_id != user.id:
        raise NotFoundError("订单不存在")
    assert_transition(order.status, OrderStatus.CANCELLED)

    for item in order.items:
        product = db.get(Product, item.product_id)
        if product is not None:
            product.stock = restore_stock(product.stock, item.quantity)  # 回补占用库存
    order.status = OrderStatus.CANCELLED
    for payment in order.payments:
        if payment.status == PaymentStatus.PENDING:
            payment.status = PaymentStatus.CLOSED
    db.commit()
    return _order_detail(db, order)


def confirm_receipt(db: Session, user: AuthUser, order_id: int) -> OrderDetail:
    order = db.get(Order, order_id)
    if order is None or order.user_id != user.id:
        raise NotFoundError("订单不存在")
    assert_transition(order.status, OrderStatus.COMPLETED)
    order.status = OrderStatus.COMPLETED
    db.commit()
    return _order_detail(db, order)


def ship_order(db: Session, order_id: int, payload: OrderShipRequest) -> OrderDetail:
    """后台发货:仅在合法的已支付 → 已发货流转中写入物流信息。"""
    order = db.get(Order, order_id)
    if order is None:
        raise NotFoundError("订单不存在")
    assert_transition(order.status, OrderStatus.SHIPPED)
    order.carrier = payload.carrier
    order.tracking_no = payload.tracking_no
    order.shipped_at = dt.datetime.now(dt.timezone.utc)
    order.status = OrderStatus.SHIPPED
    db.commit()
    return _order_detail(db, order)
