"""微信小程序 jscode2session 同步客户端。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings, settings
from app.core.exceptions import WeChatAuthError, WeChatServiceError


@dataclass(frozen=True)
class WeChatSession:
    openid: str
    unionid: str | None = None


class WeChatMpClient:
    def __init__(
        self,
        config: Settings = settings,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.config = config
        self.transport = transport

    def jscode2session(self, code: str) -> WeChatSession:
        appid = self.config.wechat_mp_appid.strip()
        appsecret = self.config.wechat_mp_appsecret.strip()
        if not appid or not appsecret:
            raise WeChatServiceError("微信小程序登录未配置")

        try:
            with httpx.Client(
                timeout=self.config.wechat_mp_timeout_seconds,
                transport=self.transport,
            ) as client:
                response = client.get(
                    self.config.wechat_mp_jscode2session_url,
                    params={
                        "appid": appid,
                        "secret": appsecret,
                        "js_code": code,
                        "grant_type": "authorization_code",
                    },
                )
                response.raise_for_status()
                data: dict[str, Any] = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise WeChatServiceError("微信登录服务暂时不可用") from exc

        if not isinstance(data, dict):
            raise WeChatServiceError("微信登录服务返回异常")
        if data.get("errcode", 0) != 0:
            raise WeChatAuthError("微信登录凭证无效或已过期")

        openid = data.get("openid")
        if not isinstance(openid, str) or not openid.strip():
            raise WeChatServiceError("微信登录服务返回异常")
        unionid = data.get("unionid")
        return WeChatSession(
            openid=openid.strip(),
            unionid=unionid.strip() if isinstance(unionid, str) and unionid.strip() else None,
        )
