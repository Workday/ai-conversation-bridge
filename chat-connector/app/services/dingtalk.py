import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class DingTalkMessage:
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
        self.allowed_users = {
            user.strip()
            for user in config.DINGTALK_ALLOWED_USERS.split(",")
            if user.strip()
        }
        self.allow_all_users = config.DINGTALK_ALLOW_ALL_USERS
        self.require_mention = config.DINGTALK_REQUIRE_MENTION
        self.group_sessions_per_user = config.DINGTALK_GROUP_SESSIONS_PER_USER

    def validate_config(self):
        return self.allow_all_users or bool(self.allowed_users)

    def parse_message(self, payload: dict) -> DingTalkMessage | None:
        if payload.get("msgtype") != "text":
            logger.info("Ignoring non-text DingTalk message.")
            return None

        text = self._extract_text(payload)
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

        return DingTalkMessage(
            msg_id=payload.get("msgId"),
            conversation_id=conversation_id,
            conversation_type=conversation_type,
            sender_user_id=sender_user_id,
            session_webhook=session_webhook,
            text=text.strip(),
            is_in_at_list=bool(payload.get("isInAtList")),
            session_id=self.get_session_id(conversation_id, conversation_type, sender_user_id),
        )

    def should_process(self, message: DingTalkMessage) -> tuple[bool, str | None]:
        if not self.validate_config():
            return False, "DingTalk allowed users not configured."

        if not self.allow_all_users and message.sender_user_id not in self.allowed_users:
            return False, f"DingTalk sender {message.sender_user_id} is not allowed."

        if message.conversation_type == "2" and self.require_mention and not message.is_in_at_list:
            return False, "DingTalk group message did not mention the bot."

        return True, None

    def get_session_id(self, conversation_id: str, conversation_type: str, sender_user_id: str) -> str:
        if conversation_type == "2" and self.group_sessions_per_user:
            return f"dingtalk:{conversation_id}:{sender_user_id}"
        return f"dingtalk:{conversation_id}"

    def send_text(self, session_webhook: str, text: str):
        payload = {
            "msgtype": "text",
            "text": {
                "content": text
            }
        }
        response = httpx.post(session_webhook, json=payload, timeout=30.0)
        response.raise_for_status()

    @staticmethod
    def _extract_text(payload: dict) -> str | None:
        text_payload = payload.get("text")
        if isinstance(text_payload, dict) and text_payload.get("content"):
            return str(text_payload.get("content"))

        content = payload.get("content")
        if content:
            return str(content)

        return None
