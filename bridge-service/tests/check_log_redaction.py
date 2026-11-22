"""Assert LINE WORKS connector logs never contain the raw user identifier.

Run: PYTHONPATH=. python tests/check_log_redaction.py
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import logging

from flask import Flask

from app.api import routes
from app.channels.lineworks.adapter import LineWorksAdapter
from app.config import Config
from app.core.idempotency import IdempotencyStore
from app.core.log_redaction import redact_identifier

SECRET = "bot-secret"
USER_ID = "7f3c9a52-raw-user-id"


class FakeClient:
    """LINE WORKS client double that accepts every send."""

    bot_secret = SECRET

    def validate_config(self) -> bool:
        return True

    def send_message(self, user_id, content):
        return None


def _post(text: str) -> None:
    client = FakeClient()
    app = Flask(__name__)
    app.extensions["lw_client"] = client
    app.extensions["lineworks_adapter"] = LineWorksAdapter(client, Config.MAX_MESSAGE_LENGTH)
    app.extensions["idempotency"] = IdempotencyStore()
    app.register_blueprint(routes.bp)

    body = json.dumps({
        "type": "message",
        "source": {"userId": USER_ID},
        "content": {"type": "text", "text": text},
    }).encode("utf-8")
    signature = base64.b64encode(
        hmac.new(SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    ).decode("utf-8")
    response = app.test_client().post(
        "/lineworks/callback",
        data=body,
        headers={"X-WORKS-Signature": signature, "Content-Type": "application/json"},
    )
    assert response.status_code == 200, response.status_code


def main() -> None:
    token = redact_identifier(USER_ID)
    assert token == redact_identifier(USER_ID), "token must be stable"
    assert token != redact_identifier("someone-else"), "token must distinguish users"
    assert USER_ID not in token
    assert redact_identifier(None) == "unknown"
    assert redact_identifier("") == "unknown"

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(handler)
    previous_level = root.level
    root.setLevel(logging.DEBUG)
    routes.get_ai_response = lambda text, session_id: "hello"  # skip the orchestrator
    try:
        _post("What is my balance?")                  # receipt + reply confirmation
        _post("x" * (Config.MAX_MESSAGE_LENGTH + 1))  # oversize warning path
    finally:
        root.removeHandler(handler)
        root.setLevel(previous_level)

    output = stream.getvalue()
    assert "Received callback from user" in output, output
    assert "Sent reply to user" in output, output
    assert "exceeds max length" in output, output
    assert USER_ID not in output, "raw user id leaked into logs"
    assert token in output, "redacted token missing from logs"

    print("log redaction checks passed")


if __name__ == "__main__":
    main()
