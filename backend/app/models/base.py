"""SQLAlchemy 2.0 声明式基类、命名约定与通用 Mixin。

- 主键统一 BIGINT GENERATED ALWAYS AS IDENTITY（除 customer_level / member_profile 之外）。
- 时间字段统一 timestamptz（DateTime(timezone=True)）。
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Identity, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# 统一约束/索引命名约定：Alembic autogenerate 与手写迁移产物保持同名。
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class IntPkMixin:
    """BIGINT 自增主键（GENERATED ALWAYS AS IDENTITY）。"""

    id: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), primary_key=True
    )


class TimestampMixin:
    """可变业务实体通用：created_at + updated_at。"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class CreatedAtMixin:
    """只追加的不可变子记录：仅 created_at。"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
