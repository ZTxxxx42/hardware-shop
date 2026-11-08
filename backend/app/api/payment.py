"""支付回调路由。仅验签,不鉴权(架构设计.md 6.2)。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.payment import PaymentNotifyPayload
from app.services import payment as payment_service

router = APIRouter(prefix="/payment", tags=["支付回调"])


@router.post("/notify/{channel}")
def payment_notify(
    channel: str,
    payload: PaymentNotifyPayload,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    # 网关要求的成功应答体,具体格式联调时按渠道调整
    payment_service.handle_notify(db, channel, payload)
    return {"code": "SUCCESS", "message": "ok"}
