"""服务层公共小工具。"""
from __future__ import annotations

from decimal import Decimal

# MVP 简化:统一运费,后续可扩展「满额包邮 / 运费模板」(架构设计.md 7.1)。
FREE_SHIPPING_THRESHOLD: Decimal = Decimal("0")


def calculate_freight(product_amount: Decimal) -> Decimal:
    """MVP 统一运费为 0;满额包邮阈值待运营配置后启用。"""
    if FREE_SHIPPING_THRESHOLD and product_amount >= FREE_SHIPPING_THRESHOLD:
        return Decimal("0")
    return Decimal("0")  # TODO: 引入统一运费后替换
