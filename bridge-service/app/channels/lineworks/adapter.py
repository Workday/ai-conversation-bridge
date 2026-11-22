"""LINE WORKS webhook adapter: signature verification and inbound parsing."""

import base64
import hashlib
import hmac
import logging

from app.channels.base import InboundMessage
from app.channels.lineworks.client import LineWorksClient
from app.core.log_redaction import redact_identifier

logger = logging.getLogger(__name__)


class LineWorksAdapter:
    """Adapter for LINE WORKS bot callbacks."""

    def __init__(self, client: LineWorksClient, max_message_length: int):
        """Store the LINE WORKS client and message length limit."""
        self.client = client
        self.max_message_length = max_message_length

    def verify_signature(self, request_body: bytes, signature: str) -> bool:
        """Verify LINE WORKS webhook signature (HMAC-SHA256 with Bot Secret).

        Returns True only when the Bot Secret is configured and signature matches.
        """
        if not self.client.bot_secret:
            logger.warning(
                "LW_API_20_BOT_SECRET not set; rejecting webhook because "
                "signature verification is unavailable."
            )
            return False

        expected = hmac.new(
            self.client.bot_secret.encode("utf-8"),
            request_body,
            hashlib.sha256
        ).digest()
        expected_b64 = base64.b64encode(expected).decode("utf-8")

        return hmac.compare_digest(expected_b64, signature)

    def session_id_for(self, user_id: str) -> str:
        """Build a platform-scoped session ID for a LINE WORKS user."""
        return f"lineworks:{user_id}"

    def idempotency_key(self, raw_body: bytes) -> str:
        """Return a SHA-256 of the raw webhook body; LINE WORKS has no event id."""
        return f"lineworks:{hashlib.sha256(raw_body).hexdigest()}"

    def parse_inbound(self, data: dict) -> InboundMessage | None:
        """Parse a LINE WORKS callback JSON body into an InboundMessage."""
        if not data or data.get('type') != 'message':
            return None

        source = data.get('source')
        user_id = source.get('userId') if source else None

        content_payload = data.get('content', {})
        message_type = content_payload.get('type')
        user_text = content_payload.get('text')

        if not user_id:
            logger.warning("No userId found in source")
            return None

        if message_type != 'text' or not isinstance(user_text, str):
            logger.info("Received non-text message or empty text.")
            return None

        user_text = user_text.strip()
        if not user_text:
            logger.info("Received non-text message or empty text.")
            return None

        if len(user_text) > self.max_message_length:
            logger.warning(
                f"Message from {redact_identifier(user_id)} exceeds max length "
                f"({len(user_text)} > {self.max_message_length})"
            )
            return InboundMessage(
                text=user_text,
                session_id=self.session_id_for(user_id),
                reply_target=user_id,
                sender_id=user_id,
            )

        return InboundMessage(
            text=user_text,
            session_id=self.session_id_for(user_id),
            reply_target=user_id,
            sender_id=user_id,
        )

    def is_over_length(self, message: InboundMessage) -> bool:
        """Return True when the inbound text exceeds the configured max length."""
        return len(message.text) > self.max_message_length
