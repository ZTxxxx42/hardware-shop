"""微信登录、注销申请与订单备注物流字段

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("openid", sa.String(length=64), nullable=True))
    op.add_column("user", sa.Column("unionid", sa.String(length=64), nullable=True))
    op.add_column(
        "user",
        sa.Column("deletion_status", sa.String(length=16), nullable=False, server_default=sa.text("'NONE'")),
    )
    op.add_column("user", sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True))
    op.create_unique_constraint("uq_user_openid", "user", ["openid"])
    op.create_index("ix_user_unionid", "user", ["unionid"])

    op.add_column("order", sa.Column("remark", sa.String(length=500), nullable=True))
    op.add_column("order", sa.Column("carrier", sa.String(length=64), nullable=True))
    op.add_column("order", sa.Column("tracking_no", sa.String(length=64), nullable=True))
    op.add_column("order", sa.Column("shipped_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("order", "shipped_at")
    op.drop_column("order", "tracking_no")
    op.drop_column("order", "carrier")
    op.drop_column("order", "remark")

    op.drop_index("ix_user_unionid", table_name="user")
    op.drop_constraint("uq_user_openid", "user", type_="unique")
    op.drop_column("user", "deletion_requested_at")
    op.drop_column("user", "deletion_status")
    op.drop_column("user", "unionid")
    op.drop_column("user", "openid")
