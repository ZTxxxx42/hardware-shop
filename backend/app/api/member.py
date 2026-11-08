"""会员路由:资料与地址。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_member
from app.core.security import AuthUser
from app.schemas.member import (
    AddressCreate,
    AddressOut,
    AddressUpdate,
    LevelOut,
    ProfileOut,
    ProfileUpdate,
)
from app.services import member as member_service

router = APIRouter(prefix="/member", tags=["会员"], dependencies=[Depends(require_member)])


@router.get("/profile", response_model=ProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> ProfileOut:
    return member_service.get_profile(db, user)


@router.patch("/profile", response_model=ProfileOut)
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> ProfileOut:
    return member_service.update_profile(db, user, payload)


@router.get("/level", response_model=LevelOut | None)
def get_level(
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> LevelOut | None:
    return member_service.get_level(db, user)


@router.get("/addresses", response_model=list[AddressOut])
def list_addresses(
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> list[AddressOut]:
    return member_service.list_addresses(db, user)


@router.post("/addresses", response_model=AddressOut, status_code=201)
def create_address(
    payload: AddressCreate,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> AddressOut:
    return member_service.create_address(db, user, payload)


@router.patch("/addresses/{address_id}", response_model=AddressOut)
def update_address(
    address_id: int,
    payload: AddressUpdate,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> AddressOut:
    return member_service.update_address(db, user, address_id, payload)


@router.delete("/addresses/{address_id}", status_code=204, response_model=None)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_member),
) -> None:
    member_service.delete_address(db, user, address_id)
