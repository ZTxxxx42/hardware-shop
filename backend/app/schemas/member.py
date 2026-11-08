"""会员资料与地址 schema。"""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ProfileOut(BaseModel):
    user_id: int
    username: str
    phone: str | None = None
    level_code: str | None = None
    level_name: str | None = None
    real_name: str | None = None


class ProfileUpdate(BaseModel):
    phone: str | None = None
    real_name: str | None = None


class AddressCreate(BaseModel):
    receiver: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=5, max_length=20)
    region: str = Field(min_length=1, max_length=200)
    detail: str = Field(min_length=1, max_length=500)


class AddressUpdate(AddressCreate):
    pass


class AddressOut(ORMModel):
    id: int
    receiver: str
    phone: str
    region: str
    detail: str


class LevelOut(BaseModel):
    code: str
    name: str
    sort: int = 0
