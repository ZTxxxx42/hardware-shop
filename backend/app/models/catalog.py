"""商品域模型：category / product / product_image / product_spec / product_price。"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, IntPkMixin, TimestampMixin


class Category(IntPkMixin, TimestampMixin, Base):
    __tablename__ = "category"

    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("category.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    parent: Mapped[Optional["Category"]] = relationship(
        back_populates="children", remote_side="Category.id"
    )
    children: Mapped[list["Category"]] = relationship(back_populates="parent")
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(IntPkMixin, TimestampMixin, Base):
    __tablename__ = "product"

    category_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("category.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retail_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="ON_SALE",
        server_default=text("'ON_SALE'"),
    )
    main_image: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    category: Mapped["Category"] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    specs: Mapped[list["ProductSpec"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    prices: Mapped[list["ProductPrice"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class ProductImage(CreatedAtMixin, IntPkMixin, Base):
    __tablename__ = "product_image"

    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("product.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    product: Mapped["Product"] = relationship(back_populates="images")


class ProductSpec(CreatedAtMixin, IntPkMixin, Base):
    __tablename__ = "product_spec"

    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("product.id", ondelete="CASCADE"), nullable=False, index=True
    )
    spec_name: Mapped[str] = mapped_column(String(128), nullable=False)
    spec_value: Mapped[str] = mapped_column(String(255), nullable=False)

    product: Mapped["Product"] = relationship(back_populates="specs")


class ProductPrice(IntPkMixin, TimestampMixin, Base):
    __tablename__ = "product_price"
    __table_args__ = (
        UniqueConstraint("product_id", "level_code", name="uq_product_price_product_level"),
    )

    # product_id 由复合唯一索引 (product_id, level_code) 覆盖，无需单独索引。
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("product.id", ondelete="CASCADE"), nullable=False
    )
    level_code: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("customer_level.code", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    product: Mapped["Product"] = relationship(back_populates="prices")
    level: Mapped["CustomerLevel"] = relationship(back_populates="product_prices")
