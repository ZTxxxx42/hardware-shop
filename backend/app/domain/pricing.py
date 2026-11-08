"""分级价格取值(架构设计.md 3.2)。

下单与展示只读 `product_price`,不运行时算折扣:
会员按 level 取 product_price,无则回退 product.retail_price;游客取零售价。
"""
from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal


def resolve_product_price(
    retail_price: Decimal,
    level_code: str | None,
    price_map: Mapping[str, Decimal],
) -> Decimal:
    if level_code and level_code in price_map:
        return price_map[level_code]
    return retail_price


def subtotal(price: Decimal, quantity: int) -> Decimal:
    return price * Decimal(quantity)
