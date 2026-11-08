"""API 总路由:挂载买家/管理/支付回调各模块。"""
from __future__ import annotations

from fastapi import APIRouter

from app.api import admin, auth, cart, catalog, member, order, payment
from app.core.config import settings

api_router = APIRouter(prefix=settings.api_prefix)

api_router.include_router(auth.router)
api_router.include_router(catalog.router)
api_router.include_router(cart.router)
api_router.include_router(order.router)
api_router.include_router(member.router)
api_router.include_router(admin.router)
api_router.include_router(payment.router)
