"""会员用例:资料、地址、等级信息。"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError, NotFoundError
from app.core.security import AuthUser
from app.models import (  # 由 database agent 提供
    Address,
    CustomerLevel,
    MemberProfile,
    User,
)
from app.schemas.member import (
    AddressCreate,
    AddressOut,
    AddressUpdate,
    LevelOut,
    ProfileOut,
    ProfileUpdate,
)


def get_profile(db: Session, user: AuthUser) -> ProfileOut:
    user_row = db.get(User, user.id)
    profile = db.scalars(select(MemberProfile).where(MemberProfile.user_id == user.id)).first()
    level = None
    if profile is not None and profile.level_code:
        level = db.scalars(
            select(CustomerLevel).where(CustomerLevel.code == profile.level_code)
        ).first()
    return ProfileOut(
        user_id=user.id,
        username=user.username,
        phone=user_row.phone if user_row else None,
        level_code=profile.level_code if profile else None,
        level_name=level.name if level else None,
        real_name=profile.real_name if profile else None,
    )


def update_profile(db: Session, user: AuthUser, payload: ProfileUpdate) -> ProfileOut:
    if payload.phone is not None:
        user_row = db.get(User, user.id)
        if user_row is not None:
            user_row.phone = payload.phone

    if payload.real_name is not None:
        profile = db.scalars(select(MemberProfile).where(MemberProfile.user_id == user.id)).first()
        if profile is None:
            # member_profile.level_code 非空且由后台指定,不允许仅凭 real_name 隐式建档
            raise BusinessError("会员档案尚未建立,请联系管理员设置等级后再完善资料")
        profile.real_name = payload.real_name

    db.commit()
    return get_profile(db, user)


def get_level(db: Session, user: AuthUser) -> LevelOut | None:
    profile = db.scalars(select(MemberProfile).where(MemberProfile.user_id == user.id)).first()
    if profile is None or not profile.level_code:
        return None
    level = db.scalars(select(CustomerLevel).where(CustomerLevel.code == profile.level_code)).first()
    if level is None:
        return None
    return LevelOut(code=level.code, name=level.name, sort=level.sort)


def list_addresses(db: Session, user: AuthUser) -> list[AddressOut]:
    rows = db.scalars(select(Address).where(Address.user_id == user.id).order_by(Address.id)).all()
    return [AddressOut.model_validate(r) for r in rows]


def create_address(db: Session, user: AuthUser, payload: AddressCreate) -> AddressOut:
    addr = Address(
        user_id=user.id,
        receiver=payload.receiver,
        phone=payload.phone,
        region=payload.region,
        detail=payload.detail,
    )
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return AddressOut.model_validate(addr)


def update_address(db: Session, user: AuthUser, address_id: int, payload: AddressUpdate) -> AddressOut:
    addr = db.get(Address, address_id)
    if addr is None or addr.user_id != user.id:
        raise NotFoundError("地址不存在")
    for field in ("receiver", "phone", "region", "detail"):
        setattr(addr, field, getattr(payload, field))
    db.commit()
    db.refresh(addr)
    return AddressOut.model_validate(addr)


def delete_address(db: Session, user: AuthUser, address_id: int) -> None:
    addr = db.get(Address, address_id)
    if addr is None or addr.user_id != user.id:
        raise NotFoundError("地址不存在")
    db.delete(addr)
    db.commit()
