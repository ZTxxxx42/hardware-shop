"""Pydantic v2 请求/响应模型。"""
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserBrief
from app.schemas.catalog import (
    CategoryOut,
    ProductBrief,
    ProductDetail,
    ProductImageOut,
    ProductPriceItem,
    ProductSpecOut,
)
from app.schemas.cart import CartItemAdd, CartItemOut, CartItemUpdate, CartSummary
from app.schemas.member import (
    AddressCreate,
    AddressOut,
    AddressUpdate,
    LevelOut,
    ProfileOut,
    ProfileUpdate,
)
from app.schemas.order import OrderCreate, OrderDetail, OrderItemOut
from app.schemas.payment import PaymentNotifyPayload, PaymentOut

__all__ = [
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserBrief",
    "CategoryOut",
    "ProductBrief",
    "ProductDetail",
    "ProductImageOut",
    "ProductPriceItem",
    "ProductSpecOut",
    "CartItemAdd",
    "CartItemOut",
    "CartItemUpdate",
    "CartSummary",
    "AddressCreate",
    "AddressOut",
    "AddressUpdate",
    "LevelOut",
    "ProfileOut",
    "ProfileUpdate",
    "OrderCreate",
    "OrderDetail",
    "OrderItemOut",
    "PaymentNotifyPayload",
    "PaymentOut",
]
