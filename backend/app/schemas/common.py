"""通用 schema。"""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMModel(BaseModel):
    """支持从 SQLAlchemy ORM 对象直接构造的响应模型基类。"""

    model_config = ConfigDict(from_attributes=True)


class PageResult(BaseModel, Generic[T]):
    total: int
    items: list[T]
