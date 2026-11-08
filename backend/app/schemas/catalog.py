"""商品目录 schema。price 字段为当前登录态视角价格。"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CategoryOut(ORMModel):
    id: int
    parent_id: int | None = None
    name: str
    sort: int = 0


class ProductPriceItem(BaseModel):
    level_code: str
    price: Decimal = Field(ge=0)


class ProductBrief(BaseModel):
    """商品列表项。游客 price=零售价,会员 price=等级价(无则回退零售价)。"""

    id: int
    category_id: int
    name: str
    model: str | None = None
    main_image: str | None = None
    retail_price: Decimal
    price: Decimal
    stock: int
    status: str


class ProductImageOut(ORMModel):
    id: int
    url: str
    sort: int = 0


class ProductSpecOut(ORMModel):
    id: int
    spec_name: str
    spec_value: str


class ProductDetail(ProductBrief):
    description: str | None = None
    images: list[ProductImageOut] = Field(default_factory=list)
    specs: list[ProductSpecOut] = Field(default_factory=list)
    # 仅管理员视角返回完整分级价格,游客/会员不泄露其他等级价
    level_prices: list[ProductPriceItem] = Field(default_factory=list)
