import json
import logging
import threading
import time
from typing import Any, Optional, Protocol

import httpx

from app.config import Config
from app.response_validator import ResponseValidator

logger = logging.getLogger(__name__)


class AIClient(Protocol):
    def get_completion(self, user_message: str, user_id: Optional[str] = None) -> str: ...


class FeishuClient:
    """Feishu Open API: tenant token + send IM messages."""

    TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    MESSAGES_URL = "https://open.feishu.cn/open-apis/im/v1/messages"

    def __init__(self, app_id: Optional[str], app_secret: Optional[str]):
        self._app_id = app_id
        self._app_secret = app_secret
        self._token: Optional[str] = None
        self._token_expire_at_ms: float = 0.0
        self._lock = threading.Lock()

    def validate_config(self) -> bool:
        return bool(self._app_id and self._app_secret)

    def get_tenant_access_token(self) -> str:
        now = time.time() * 1000
        with self._lock:
            if self._token and now < self._token_expire_at_ms - 60_000:
                return self._token

        if not self.validate_config():
            raise RuntimeError("FEISHU_APP_ID or FEISHU_APP_SECRET missing")

        payload = {"app_id": self._app_id, "app_secret": self._app_secret}
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                self.TOKEN_URL,
                headers={"Content-Type": "application/json; charset=utf-8"},
                json=payload,
            )
            r.raise_for_status()
            data = r.json()

        if data.get("code") != 0:
            raise RuntimeError(f"Feishu token API error: {data.get('msg')}")

        token = data["tenant_access_token"]
        expire_sec = int(data.get("expire", 7200))
        with self._lock:
            self._token = token
            self._token_expire_at_ms = time.time() * 1000 + expire_sec * 1000
        logger.info("Tenant access token refreshed")
        return token

    def send_text_to_chat(self, chat_id: str, text: str, timeout: float = 10.0) -> dict[str, Any]:
        token = self.get_tenant_access_token()
        url = f"{self.MESSAGES_URL}?receive_id_type=chat_id"
        body = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False),
        }
        with httpx.Client(timeout=timeout) as client:
            r = client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            r.raise_for_status()
            return r.json()


def _sender_id_from_event(event: dict[str, Any]) -> Optional[str]:
    """Resolve sender id across user_id, open_id, and union_id."""
    sender_id = (event.get("sender") or {}).get("sender_id") or {}
    return (
        sender_id.get("user_id")
        or sender_id.get("open_id")
        or sender_id.get("union_id")
    )


def _parse_text_content(raw_content: Any) -> str:
    if not raw_content:
        return ""
    if isinstance(raw_content, dict):
        return str(raw_content.get("text") or "").strip()
    try:
        content_json = json.loads(str(raw_content))
        return str(content_json.get("text") or "").strip()
    except (json.JSONDecodeError, TypeError):
        return str(raw_content).strip()


def process_im_text_message(
    *,
    event: dict[str, Any],
    feishu: FeishuClient,
    ai_client: AIClient,
) -> None:
    """Handle a Feishu im.message.receive_v1 text event (runs outside request context)."""
    message = event.get("message") or {}
    if message.get("message_type") != "text":
        logger.info("Ignoring non-text message (%s)", message.get("message_type"))
        return

    chat_id = message.get("chat_id")
    if not chat_id:
        logger.error("Missing chat_id on Feishu message")
        return

    sender_id = _sender_id_from_event(event)
    user_message = _parse_text_content(message.get("content"))
    if not user_message:
        logger.warning("Empty user message; skipping")
        return

    if len(user_message) > Config.MAX_MESSAGE_LENGTH:
        try:
            feishu.send_text_to_chat(
                chat_id,
                f"Your message is too long. Please keep it under "
                f"{Config.MAX_MESSAGE_LENGTH} characters.",
            )
        except httpx.HTTPError as e:
            logger.error("Failed to send length limit message: %s", e)
        return

    logger.info('Feishu user %s in chat %s: "%s"', sender_id or "unknown", chat_id, user_message)

    if not feishu.validate_config():
        logger.error("Feishu configuration incomplete")
        return

    # Flowise/OpenRouter session key: stable per chat (same pattern as LINE WORKS user_id).
    session_key = chat_id

    try:
        ai_raw = ai_client.get_completion(user_message, user_id=session_key)
        ai_reply = ResponseValidator.validate(str(ai_raw or ""), user_message=user_message)
        send_result = feishu.send_text_to_chat(chat_id, ai_reply)
        if isinstance(send_result, dict) and send_result.get("code") != 0:
            logger.error("Feishu send returned error payload: %s", send_result)
    except httpx.HTTPError as e:
        logger.error("Feishu HTTP error while processing message: %s", e)
        try:
            feishu.send_text_to_chat(
                chat_id,
                "Sorry, an error occurred while processing your request. "
                "Please try again later or contact support.",
            )
        except httpx.HTTPError as send_err:
            logger.error("Failed to send error message: %s", send_err)
