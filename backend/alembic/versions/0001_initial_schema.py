"""initial schema：13 张表 + 索引 + 约束

与 backend/app/models 严格一致，由数据库 agent 手写（非 autogenerate）。
主键：BIGINT GENERATED ALWAYS AS IDENTITY（customer_level 用 code、member_profile 用 user_id 共享主键除外）。

Revision ID: 0001
Revises:
Create Date: 2026-11-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. user
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False, server_default=sa.text("'member'")),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("username", name="uq_user_username"),
    )

    # 2. customer_level（code 为自然主键，无自增 id）
    op.create_table(
        "customer_level",
        sa.Column("code", sa.String(length=32), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
    )

    # 3. member_profile（与 user 1:1，共享主键 user_id）
    op.create_table(
        "member_profile",
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "level_code",
            sa.String(length=32),
            sa.ForeignKey("customer_level.code", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("real_name", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_member_profile_level_code", "member_profile", ["level_code"])

    # 4. category（自引用多级分类）
    op.create_table(
        "category",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "parent_id",
            sa.BigInteger(),
            sa.ForeignKey("category.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_category_parent_id", "category", ["parent_id"])

    # 5. product
    op.create_table(
        "product",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "category_id",
            sa.BigInteger(),
            sa.ForeignKey("category.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("retail_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default=sa.text("'ON_SALE'")),
        sa.Column("main_image", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_product_category_id", "product", ["category_id"])

    # 6. product_image
    op.create_table(
        "product_image",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "product_id",
            sa.BigInteger(),
            sa.ForeignKey("product.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_product_image_product_id", "product_image", ["product_id"])

    # 7. product_spec
    op.create_table(
        "product_spec",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "product_id",
            sa.BigInteger(),
            sa.ForeignKey("product.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("spec_name", sa.String(length=128), nullable=False),
        sa.Column("spec_value", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_product_spec_product_id", "product_spec", ["product_id"])

    # 8. product_price（分级价格）
    op.create_table(
        "product_price",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "product_id",
            sa.BigInteger(),
            sa.ForeignKey("product.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "level_code",
            sa.String(length=32),
            sa.ForeignKey("customer_level.code", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("product_id", "level_code", name="uq_product_price_product_level"),
    )
    # 复合唯一索引 (product_id, level_code) 已覆盖 product_id；level_code 单独建索引。
    op.create_index("ix_product_price_level_code", "product_price", ["level_code"])

    # 9. cart_item
    op.create_table(
        "cart_item",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.BigInteger(),
            sa.ForeignKey("product.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_cart_item_user_id", "cart_item", ["user_id"])
    op.create_index("ix_cart_item_product_id", "cart_item", ["product_id"])

    # 10. address
    op.create_table(
        "address",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("receiver", sa.String(length=64), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("region", sa.String(length=255), nullable=False),
        sa.Column("detail", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_address_user_id", "address", ["user_id"])

    # 11. order（SQL 保留字，需加引号；SQLAlchemy 方言自动处理）
    op.create_table(
        "order",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("order_no", sa.String(length=32), nullable=False),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("user.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'PENDING_PAYMENT'")),
        sa.Column("product_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("freight_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("receiver_name", sa.String(length=64), nullable=False),
        sa.Column("receiver_phone", sa.String(length=20), nullable=False),
        sa.Column("receiver_region", sa.String(length=255), nullable=False),
        sa.Column("receiver_detail", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("order_no", name="uq_order_order_no"),
    )
    op.create_index("ix_order_user_id", "order", ["user_id"])
    op.create_index("ix_order_status", "order", ["status"])

    # 12. order_item
    op.create_table(
        "order_item",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "order_id",
            sa.BigInteger(),
            sa.ForeignKey("order.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.BigInteger(),
            sa.ForeignKey("product.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_order_item_order_id", "order_item", ["order_id"])
    op.create_index("ix_order_item_product_id", "order_item", ["product_id"])

    # 13. payment
    op.create_table(
        "payment",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "order_id",
            sa.BigInteger(),
            sa.ForeignKey("order.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(length=16), nullable=False),
        sa.Column("trade_no", sa.String(length=64), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("order_id", "channel", name="uq_payment_order_channel"),
    )
    # 复合唯一索引 (order_id, channel) 已覆盖 order_id；status 单独建索引。
    op.create_index("ix_payment_status", "payment", ["status"])


def downgrade() -> None:
    op.drop_table("payment")
    op.drop_table("order_item")
    op.drop_table("order")
    op.drop_table("address")
    op.drop_table("cart_item")
    op.drop_table("product_price")
    op.drop_table("product_spec")
    op.drop_table("product_image")
    op.drop_table("product")
    op.drop_table("category")
    op.drop_table("member_profile")
    op.drop_table("customer_level")
    op.drop_table("user")
