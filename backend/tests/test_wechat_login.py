import httpx
import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.exceptions import WeChatAuthError, WeChatServiceError
from app.schemas.auth import WeChatLoginRequest
from app.services.wechat import WeChatMpClient


def make_settings(appid: str = "appid", appsecret: str = "secret") -> Settings:
    return Settings(
        _env_file=None,
        wechat_mp_appid=appid,
        wechat_mp_appsecret=appsecret,
    )


@pytest.mark.parametrize(("appid", "appsecret"), [("", "secret"), ("appid", ""), (" ", " ")])
def test_wechat_login_fails_closed_when_not_configured(appid: str, appsecret: str) -> None:
    client = WeChatMpClient(make_settings(appid, appsecret))
    with pytest.raises(WeChatServiceError) as exc_info:
        client.jscode2session("valid-code")
    assert exc_info.value.status_code == 503


def test_wechat_login_rejects_blank_code() -> None:
    with pytest.raises(ValidationError):
        WeChatLoginRequest(code="  ")


def test_wechat_error_response_is_unauthorized() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"errcode": 40029, "errmsg": "invalid code"})
    )
    client = WeChatMpClient(make_settings(), transport=transport)
    with pytest.raises(WeChatAuthError) as exc_info:
        client.jscode2session("invalid-code")
    assert exc_info.value.status_code == 401


def test_wechat_upstream_failure_is_service_unavailable() -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("upstream unavailable", request=request)

    client = WeChatMpClient(make_settings(), transport=httpx.MockTransport(fail))
    with pytest.raises(WeChatServiceError) as exc_info:
        client.jscode2session("valid-code")
    assert exc_info.value.status_code == 503
