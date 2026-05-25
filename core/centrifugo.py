from __future__ import annotations

import logging
import time
from typing import Any

import jwt
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def make_connection_token(
    user_id: int | str,
    *,
    subs: dict[str, dict] | None = None,
) -> str:

    payload: dict[str, Any] = {
        "sub": str(user_id) if user_id else "",
        "exp": int(time.time()) + int(settings.CENTRIFUGO_TOKEN_TTL),
    }
    if subs:
        payload["subs"] = subs
    token = jwt.encode(
        payload,
        settings.CENTRIFUGO_HMAC_SECRET_KEY,
        algorithm="HS256",
    )
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def question_channel(question_id: int) -> str:
    return f"{settings.CENTRIFUGO_NAMESPACE}:question.{question_id}"


def publish(channel: str, data: dict) -> bool:
    url = settings.CENTRIFUGO_API_URL.rstrip("/") + "/publish"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": settings.CENTRIFUGO_API_KEY,
    }
    body = {"channel": channel, "data": data}
    try:
        response = requests.post(url, json=body, headers=headers, timeout=5)
    except requests.RequestException:
        logger.exception("centrifugo publish %s: ошибка сети", channel)
        return False
    if response.status_code != 200:
        logger.warning(
            "centrifugo publish %s: status=%s body=%s",
            channel,
            response.status_code,
            response.text[:300],
        )
        return False
    return True
