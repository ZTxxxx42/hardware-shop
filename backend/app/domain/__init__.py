"""领域层:纯业务规则,独立可测,不依赖 ORM/HTTP。"""
from app.domain.inventory import assert_stock_sufficient, deduct_stock, restore_stock
from app.domain.order_state import OrderStatus, assert_transition, can_transition, next_statuses
from app.domain.payment import PaymentChannel, PaymentStatus, is_success_payment
from app.domain.pricing import resolve_product_price, subtotal

__all__ = [
    "OrderStatus",
    "can_transition",
    "assert_transition",
    "next_statuses",
    "resolve_product_price",
    "subtotal",
    "assert_stock_sufficient",
    "deduct_stock",
    "restore_stock",
    "PaymentChannel",
    "PaymentStatus",
    "is_success_payment",
]
