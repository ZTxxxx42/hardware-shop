"""认证相关 schema。"""
from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.schemas.common import ORMModel


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    phone: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class WeChatLoginRequest(BaseModel):
    code: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=128),
    ]


class UserBrief(ORMModel):
    id: int
    username: str
    role: str
    phone: str | None = None
    level_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserBrief
