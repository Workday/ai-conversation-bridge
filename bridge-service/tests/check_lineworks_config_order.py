"""Assert the LINE WORKS callback validates config before any outbound reply.

Run: PYTHONPATH=. python tests/check_lineworks_config_order.py
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json

from flask import Flask

from app.api.routes import bp
from app.channels.lineworks.adapter import LineWorksAdapter
from app.config import Config
from app.core.idempotency import IdempotencyStore

SECRET = "bot-secret"


class FakeClient:
    """LINE WORKS client double that records outbound sends."""

    bot_secret = SECRET

    def __init__(self, configured: bool):
        self.configured = configured
        self.attempts = 0
        self.sent: list[tuple[str, dict]] = []

    def validate_config(self) -> bool:
        return self.configured

    def send_message(self, user_id, content):
        self.attempts += 1
        if not self.configured:
            raise RuntimeError("send_message called with incomplete LINE WORKS config")
        self.sent.append((user_id, content))


def _post_oversize(configured: bool):
    client = FakeClient(configured)
    app = Flask(__name__)
    app.extensions["lw_client"] = client
    app.extensions["lineworks_adapter"] = LineWorksAdapter(client, Config.MAX_MESSAGE_LENGTH)
    app.extensions["idempotency"] = IdempotencyStore()
    app.register_blueprint(bp)

    body = json.dumps({
        "type": "message",
        "source": {"userId": "u1"},
        "content": {"type": "text", "text": "x" * (Config.MAX_MESSAGE_LENGTH + 1)},
    }).encode("utf-8")
    signature = base64.b64encode(
        hmac.new(SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    ).decode("utf-8")
    response = app.test_client().post(
        "/lineworks/callback",
        data=body,
        headers={"X-WORKS-Signature": signature, "Content-Type": "application/json"},
    )
    return response, client


def main() -> None:
    # Incomplete config: no outbound call may be attempted, and the failure is
    # reported by the explicit config check rather than an exception in send.
    response, client = _post_oversize(configured=False)
    assert response.status_code == 500, response.status_code
    assert client.attempts == 0, "send_message ran before validate_config"
    assert client.sent == []

    # Complete config: the oversize warning is still delivered.
    response, client = _post_oversize(configured=True)
    assert response.status_code == 200, response.status_code
    assert len(client.sent) == 1 and client.sent[0][0] == "u1", client.sent

    print("lineworks config order checks passed")


if __name__ == "__main__":
    main()
