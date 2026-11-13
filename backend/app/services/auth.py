"""认证用例:注册、登录、签发 token。"""
from __future__ import annotations

import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BusinessError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User  # 由 database agent 提供
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserBrief,
    WeChatLoginRequest,
)
from app.services.wechat import WeChatMpClient


def _level_code(user: User) -> str | None:
    return getattr(getattr(user, "profile", None), "level_code", None)


def _issue_token(user: User) -> TokenResponse:
    level_code = _level_code(user)
    token = create_access_token(user.id, user.role, level_code)
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserBrief(
            id=user.id,
            username=user.username,
            role=user.role,
            phone=getattr(user, "phone", None),
            level_code=level_code,
        ),
    )


def register(db: Session, payload: RegisterRequest) -> TokenResponse:
    exists = db.scalars(select(User).where(User.username == payload.username)).first()
    if exists is not None:
        raise BusinessError("用户名已存在")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role="member",
        phone=payload.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # TODO: 会员等级由后台指定(架构设计.md 7.1「固定 3 级、后台人工指定」),
    # 注册时不创建 member_profile,level_code 为空 → 价格回退零售价,符合 3.2。
    return _issue_token(user)


def login(db: Session, payload: LoginRequest) -> TokenResponse:
    user = db.scalars(select(User).where(User.username == payload.username)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise BusinessError("用户名或密码错误")
    return _issue_token(user)


def wechat_login(
    db: Session,
    payload: WeChatLoginRequest,
    client: WeChatMpClient | None = None,
) -> TokenResponse:
    session = (client or WeChatMpClient()).jscode2session(payload.code)
    user = db.scalars(select(User).where(User.openid == session.openid)).first()
    if user is None:
        user = User(
            username=f"wx_{secrets.token_urlsafe(18)}",
            password_hash=hash_password(secrets.token_urlsafe(48)),
            role="member",
            openid=session.openid,
            unionid=session.unionid,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif session.unionid and user.unionid != session.unionid:
        user.unionid = session.unionid
        db.commit()
    return _issue_token(user)
