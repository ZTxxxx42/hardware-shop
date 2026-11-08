"""应用层统一异常。

领域层/服务层抛出这些异常,表现层由 main.py 全局处理器统一转换为 JSON 响应,
避免路由内散布 try/except。
"""
from __future__ import annotations


class AppError(Exception):
    """业务异常基类。"""

    status_code: int = 400
    code: str = "APP_ERROR"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class BusinessError(AppError):
    status_code = 400
    code = "BUSINESS_ERROR"


class InsufficientStockError(BusinessError):
    code = "INSUFFICIENT_STOCK"


class InvalidStateTransitionError(BusinessError):
    code = "INVALID_STATE_TRANSITION"


class PaymentVerifyError(BusinessError):
    code = "PAYMENT_VERIFY_FAILED"
