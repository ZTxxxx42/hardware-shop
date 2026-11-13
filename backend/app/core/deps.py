"""FastAPI 依赖注入:数据库会话与接口级鉴权。

约定:database agent 在 `app.models` 暴露 `Base` 及全部 ORM 模型;
会话工厂由 `app.core.db` 提供,本模块只 import、不定义(避免与 database agent 冲突)。
"""
from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.security import AuthUser, decode_token
from app.models import User  # 由 database agent 提供

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _auth_user_from_credentials(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> AuthUser:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "未提供登录凭证")
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "登录凭证无效或已过期")

    user_id = int(payload.get("sub", "0"))
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户不存在")

    level_code = getattr(getattr(user, "profile", None), "level_code", None)
    return AuthUser(
        id=user.id,
        username=user.username,
        role=user.role,
        level_code=level_code,
        phone=getattr(user, "phone", None),
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthUser:
    return _auth_user_from_credentials(credentials, db)


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthUser | None:
    """价格接口按登录态动态返回(游客零售价 / 会员等级价),允许未登录访问。"""
    if credentials is None:
        return None
    try:
        return _auth_user_from_credentials(credentials, db)
    except HTTPException:
        return None


def require_member(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if user.role != "member":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "仅会员可访问")
    return user


def require_admin(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "仅管理员可访问")
    return user
