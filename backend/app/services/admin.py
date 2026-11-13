"""管理端用例:客户列表与等级指定。

客户管理属于后台运营(role=admin),但操作对象是前台会员(User + MemberProfile),
因此复用会员的 ProfileOut 作为响应契约,仅在此编排跨表查询与建档逻辑。
"""
from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import (  # 由 database agent 提供
    CustomerLevel,
    MemberProfile,
    User,
)
from app.schemas.member import ProfileOut


def _profile_out(user: User, profile: MemberProfile | None, level: CustomerLevel | None) -> ProfileOut:
    return ProfileOut(
        user_id=user.id,
        username=user.username,
        phone=user.phone,
        level_code=profile.level_code if profile else None,
        level_name=level.name if level else None,
        real_name=profile.real_name if profile else None,
    )


def list_customers(db: Session, keyword: str | None = None) -> list[ProfileOut]:
    """返回所有 role=member 的用户,关联会员档案与等级字典;keyword 模糊匹配账号/手机/姓名。"""
    stmt = (
        select(User, MemberProfile, CustomerLevel)
        .outerjoin(MemberProfile, MemberProfile.user_id == User.id)
        .outerjoin(CustomerLevel, CustomerLevel.code == MemberProfile.level_code)
        .where(User.role == "member")
        .order_by(User.id)
    )
    if keyword and keyword.strip():
        pattern = f"%{keyword.strip()}%"
        stmt = stmt.where(
            or_(
                User.username.ilike(pattern),
                User.phone.ilike(pattern),
                MemberProfile.real_name.ilike(pattern),
            )
        )
    return [_profile_out(user, profile, level) for user, profile, level in db.execute(stmt).all()]


def set_customer_level(db: Session, user_id: int, level_code: str) -> ProfileOut:
    """为客户指定会员等级:已有档案则更新,否则建档;仅允许操作会员账号。"""
    user = db.get(User, user_id)
    if user is None or user.role != "member":
        raise NotFoundError("客户不存在")

    level = db.get(CustomerLevel, level_code)
    if level is None:
        raise NotFoundError("客户等级不存在")

    profile = db.scalars(select(MemberProfile).where(MemberProfile.user_id == user_id)).first()
    if profile is None:
        profile = MemberProfile(user_id=user_id, level_code=level_code)
        db.add(profile)
    else:
        profile.level_code = level_code

    db.commit()
    return _profile_out(user, profile, level)
