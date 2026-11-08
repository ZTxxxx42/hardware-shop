"""安全:JWT 生成/校验 + bcrypt 密码哈希。

JWT 无状态认证(架构设计.md 第 5 节):payload 携带 sub/role/level_code。
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

ALGORITHM = settings.jwt_algorithm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass(frozen=True)
class AuthUser:
    """依赖注入后的当前登录用户视图。"""

    id: int
    username: str
    role: str
    level_code: str | None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except ValueError:
        # 哈希格式非法时按校验失败处理,避免 500
        return False


def create_access_token(
    user_id: int,
    role: str,
    level_code: str | None = None,
    expires_delta: dt.timedelta | None = None,
) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    expire = now + (expires_delta or dt.timedelta(minutes=settings.access_token_expire_minutes))
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": expire,
    }
    if level_code:
        payload["level_code"] = level_code
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """校验签名与过期时间,失败时抛 jwt 异常,由调用方转换为 401。"""
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
