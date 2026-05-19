"""DingTalk HTTP-mode robot webhook adapter."""

import logging
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

# Only allow replies to be sent back to known DingTalk session-webhook hosts.
# This prevents SSRF where a forged callback supplies an attacker-controlled
# `sessionWebhook` URL (e.g. a cloud metadata endpoint or internal service).
ALLOWED_SESSION_WEBHOOK_HOSTS = frozenset({
    "oapi.dingtalk.com",
    "api.dingtalk.com",
})


def is_allowed_session_webhook(url: str) -> bool:
    """Return True if `url` is an https URL on a known DingTalk session-webhook host."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme != "https":
        return False
    return parsed.hostname in ALLOWED_SESSION_WEBHOOK_HOSTS


@dataclass
class DingTalkMessage:
    """Normalized fields parsed from a DingTalk robot callback payload."""

    msg_id: str | None
    conversation_id: str
    conversation_type: str
    sender_user_id: str
    session_webhook: str
    text: str
    is_in_at_list: bool
    session_id: str


class DingTalkClient:
    """DingTalk HTTP-mode robot adapter."""

    def __init__(self, config):
        """Load DingTalk access-control settings from the application config."""
        self.allowed_users = {
            user.strip()
            for user in config.DINGTALK_ALLOWED_USERS.split(",")
            if user.strip()
        }
        self.allow_all_users = config.DINGTALK_ALLOW_ALL_USERS
        self.require_mention = config.DINGTALK_REQUIRE_MENTION
        self.group_sessions_per_user = config.DINGTALK_GROUP_SESSIONS_PER_USER

    def validate_config(self):
        """Return True when at least one allowed-user policy is configured."""
        return self.allow_all_users or bool(self.allowed_users)

    def parse_message(self, payload: dict) -> DingTalkMessage | None:
        """Parse and validate a DingTalk callback payload into a DingTalkMessage."""
        if payload.get("msgtype") != "text":
            logger.info("Ignoring non-text DingTalk message.")
            return None

        text = self._extract_text(payload)
        text = text.strip() if text else ""
        if not text:
            logger.info("Ignoring DingTalk message without text content.")
            return None

        conversation_id = payload.get("conversationId")
        conversation_type = str(payload.get("conversationType", ""))
        sender_user_id = payload.get("senderStaffId")
        encrypted_sender_id = payload.get("senderId")
        session_webhook = payload.get("sessionWebhook")

        if not conversation_id:
            logger.warning("Ignoring DingTalk message without conversationId.")
            return None
        if not sender_user_id:
            logger.warning(
                "Ignoring DingTalk message without senderStaffId. "
                "Publish both the DingTalk app version and robot capability, then install "
                "the internal-app robot in an internal group so DingTalk sends the "
                "admin-console UserID. senderId=%s conversationType=%s",
                encrypted_sender_id,
                conversation_type,
            )
            return None
        if not session_webhook:
            logger.warning("Ignoring DingTalk message without sessionWebhook.")
            return None
        if not is_allowed_session_webhook(session_webhook):
            logger.warning(
                "Ignoring DingTalk message with sessionWebhook outside the allowed "
                "DingTalk hosts. host=%s",
                urlparse(session_webhook).hostname,
            )
            return None

        return DingTalkMessage(
            msg_id=payload.get("msgId"),
            conversation_id=conversation_id,
            conversation_type=conversation_type,
            sender_user_id=sender_user_id,
            session_webhook=session_webhook,
            text=text,
            is_in_at_list=bool(payload.get("isInAtList")),
            session_id=self.get_session_id(conversation_id, conversation_type, sender_user_id),
        )

    def should_process(self, message: DingTalkMessage) -> tuple[bool, str | None]:
        """Return whether the message should be handled and an optional skip reason."""
        if not self.validate_config():
            return False, "DingTalk allowed users not configured."

        if not self.allow_all_users and message.sender_user_id not in self.allowed_users:
            return False, f"DingTalk sender {message.sender_user_id} is not allowed."

        if message.conversation_type == "2" and self.require_mention and not message.is_in_at_list:
            return False, "DingTalk group message did not mention the bot."

        return True, None

    def get_session_id(self, conversation_id: str, conversation_type: str, sender_user_id: str) -> str:
        """Build a platform-scoped AI session ID for the conversation."""
        if conversation_type == "2" and self.group_sessions_per_user:
            return f"dingtalk:{conversation_id}:{sender_user_id}"
        return f"dingtalk:{conversation_id}"

    def generate_title_from_text(self, text: str, max_length: int = 50) -> str:
        """Derive a short Markdown title from the first line of a reply."""
        # 1. Take the first line (works for Chinese, English, etc.)
        first_line = text.split('\n')[0].strip()
        # 2. Remove leading Markdown heading markers like #, ##, ###
        first_line = re.sub(r'^#{1,6}\s*', '', first_line)
        # 3. Truncate to max length
        return first_line[:max_length].rstrip()

    def send_text(self, session_webhook: str, text: str):
        """Send a Markdown reply through DingTalk's per-session webhook URL."""
        # Defense in depth: parse_message already enforces this, but reject here
        # in case callers ever bypass parse_message.
        if not is_allowed_session_webhook(session_webhook):
            raise ValueError("Refusing to POST to non-DingTalk session webhook host.")
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": self.generate_title_from_text(text),
                "text": text
            }
        }
        response = httpx.post(session_webhook, json=payload, timeout=30.0)
        response.raise_for_status()

    @staticmethod
    def _extract_text(payload: dict) -> str | None:
        """Extract text content from the canonical DingTalk text message payload."""
        text_payload = payload.get("text")
        if isinstance(text_payload, dict) and text_payload.get("content"):
            return str(text_payload.get("content"))
        return None
