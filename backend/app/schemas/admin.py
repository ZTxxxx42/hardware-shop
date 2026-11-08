"""后台管理 schema(admin)。"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.catalog import ProductPriceItem


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    parent_id: int | None = None
    sort: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None
    sort: int | None = None


class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=200)
    model: str | None = None
    description: str | None = None
    retail_price: Decimal = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    status: str = "ON_SALE"
    main_image: str | None = None


class ProductUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = None
    model: str | None = None
    description: str | None = None
    retail_price: Decimal | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    status: str | None = None
    main_image: str | None = None


class ProductPriceUpsert(BaseModel):
    """按等级批量设置价格,展开写入 product_price 冗余落库(架构设计.md 3.2)。"""

    prices: list[ProductPriceItem]
