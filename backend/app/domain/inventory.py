"""库存扣减/回补纯规则。"""
from __future__ import annotations

from app.core.exceptions import InsufficientStockError


def assert_stock_sufficient(stock: int, quantity: int) -> None:
    if quantity <= 0 or stock < quantity:
        raise InsufficientStockError(f"库存不足:当前 {stock},需求 {quantity}")


def deduct_stock(stock: int, quantity: int) -> int:
    assert_stock_sufficient(stock, quantity)
    return stock - quantity


def restore_stock(stock: int, quantity: int) -> int:
    return stock + quantity
