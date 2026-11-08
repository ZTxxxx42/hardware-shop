"""用户域模型：user / customer_level / member_profile / address。"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPkMixin, TimestampMixin


class User(IntPkMixin, TimestampMixin, Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="member",
        server_default=text("'member'"),
    )
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    profile: Mapped[Optional["MemberProfile"]] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class CustomerLevel(Base):
    """客户等级字典，code 为自然主键：retail / wholesale / vip。"""

    __tablename__ = "customer_level"

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    member_profiles: Mapped[list["MemberProfile"]] = relationship(back_populates="level")
    product_prices: Mapped[list["ProductPrice"]] = relationship(back_populates="level")


class MemberProfile(TimestampMixin, Base):
    """会员资料，与 user 1:1（共享主键 user_id）。"""

    __tablename__ = "member_profile"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    level_code: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("customer_level.code", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    real_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")
    level: Mapped["CustomerLevel"] = relationship(back_populates="member_profiles")


class Address(IntPkMixin, TimestampMixin, Base):
    __tablename__ = "address"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    region: Mapped[str] = mapped_column(String(255), nullable=False)
    detail: Mapped[str] = mapped_column(String(512), nullable=False)

    user: Mapped["User"] = relationship(back_populates="addresses")
