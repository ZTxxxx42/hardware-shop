"""应用配置(pydantic-settings)。环境变量经 .env 注入。"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "五金商贸 API"
    debug: bool = False
    api_prefix: str = "/api"

    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/hardware_shop"

    # 前端开发服务白名单,JSON 数组格式
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ]

    # 微信小程序静默登录；空配置时接口失败关闭。
    wechat_mp_appid: str = ""
    wechat_mp_appsecret: str = ""
    wechat_mp_jscode2session_url: str = "https://api.weixin.qq.com/sns/jscode2session"
    wechat_mp_timeout_seconds: float = 5.0

    # 支付网关占位(MVP 联调时替换为真实商户配置)
    wechat_pay_api_v3_key: str = ""
    alipay_app_private_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
