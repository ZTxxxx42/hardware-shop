"""订单域模型：order / order_item / payment。"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, IntPkMixin, TimestampMixin


class Order(IntPkMixin, TimestampMixin, Base):
    """订单主表。order 为 SQL 保留字，SQLAlchemy 会为表名加引号。"""

    __tablename__ = "order"

    order_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="PENDING_PAYMENT",
        server_default=text("'PENDING_PAYMENT'"),
        index=True,
    )
    product_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0, server_default="0"
    )
    freight_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0, server_default="0"
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0, server_default="0"
    )
    # 收货地址快照（下单时固化，防止后续地址修改影响历史订单）。
    receiver_name: Mapped[str] = mapped_column(String(64), nullable=False)
    receiver_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    receiver_region: Mapped[str] = mapped_column(String(255), nullable=False)
    receiver_detail: Mapped[str] = mapped_column(String(512), nullable=False)
    remark: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    carrier: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    tracking_no: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    shipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class OrderItem(CreatedAtMixin, IntPkMixin, Base):
    __tablename__ = "order_item"

    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("order.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # 商品删除后订单项保留，product_id 置空，名称/单价快照仍可展示。
    product_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("product.id", ondelete="SET NULL"), nullable=True, index=True
    )
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped[Optional["Product"]] = relationship(back_populates="order_items")


class Payment(CreatedAtMixin, IntPkMixin, Base):
    __tablename__ = "payment"
    __table_args__ = (
        UniqueConstraint("order_id", "channel", name="uq_payment_order_channel"),
    )

    # order_id 由复合唯一索引 (order_id, channel) 覆盖，无需单独索引。
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("order.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(16), nullable=False)
    trade_no: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="PENDING",
        server_default=text("'PENDING'"),
        index=True,
    )
    # 支付成功时间：成功前为 NULL，不设 server_default，由回调成功时写入。
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    order: Mapped["Order"] = relationship(back_populates="payments")
