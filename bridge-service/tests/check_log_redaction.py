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

from app.api import routes
from app.channels.lineworks import client as lw_client_module
from app.channels.lineworks.adapter import LineWorksAdapter
from app.channels.lineworks.client import LineWorksClient
from app.config import Config
from app.core.idempotency import IdempotencyStore
from app.core.log_redaction import redact_identifier, redact_user_paths
from flask import Flask

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
    assert len(token) == len("user-") + 16, token

    # httpx logs the send URL, which carries the raw id; the filter rewrites it.
    url = f"https://www.worksapis.com/v1.0/bots/123/users/{USER_ID}/messages"
    assert redact_user_paths(url) == f"https://www.worksapis.com/v1.0/bots/123/users/{token}/messages"
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.addHandler(handler)
    previous_httpx_level = httpx_logger.level
    httpx_logger.setLevel(logging.INFO)
    try:
        httpx_logger.info('HTTP Request: %s %s "%s %d %s"', "POST", url, "HTTP/1.1", 200, "OK")
    finally:
        httpx_logger.removeHandler(handler)
        httpx_logger.setLevel(previous_httpx_level)
    assert USER_ID not in stream.getvalue() and token in stream.getvalue(), stream.getvalue()

    # A failed send raises without the URL (and so without the raw id).
    lw = LineWorksClient(Config)
    lw.get_access_token = lambda: "test-token"
    real_post = lw_client_module.httpx.post
    lw_client_module.httpx.post = lambda url, **kw: lw_client_module.httpx.Response(
        404, request=lw_client_module.httpx.Request("POST", url)
    )
    try:
        lw.send_message(USER_ID, {"content": {"type": "text", "text": "hi"}})
        raise AssertionError("send_message should raise on HTTP 404")
    except RuntimeError as exc:
        assert USER_ID not in str(exc) and token in str(exc) and "404" in str(exc), exc
    finally:
        lw_client_module.httpx.post = real_post

    print("log redaction checks passed")


if __name__ == "__main__":
    main()
