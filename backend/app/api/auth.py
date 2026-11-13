"""认证路由。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.security import AuthUser
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserBrief,
    WeChatLoginRequest,
)
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.register(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.login(db, payload)


@router.post("/wechat/login", response_model=TokenResponse)
def wechat_login(payload: WeChatLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.wechat_login(db, payload)


@router.get("/me", response_model=UserBrief)
def me(user: AuthUser = Depends(get_current_user)) -> UserBrief:
    return UserBrief(
        id=user.id,
        username=user.username,
        role=user.role,
        phone=user.phone,
        level_code=user.level_code,
    )
