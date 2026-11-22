"""Assert LINE WORKS webhook signature verification fails closed.

Run: PYTHONPATH=. python tests/check_lineworks_signature.py
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

_ADAPTER = Path(__file__).resolve().parents[1] / "app" / "channels" / "lineworks" / "adapter.py"


def _load_adapter():
    """Load LineWorksAdapter without importing app (Flask is a runtime dep)."""
    base_module = types.ModuleType("app.channels.base")
    base_module.InboundMessage = object
    client_module = types.ModuleType("app.channels.lineworks.client")
    client_module.LineWorksClient = object
    redaction_module = types.ModuleType("app.core.log_redaction")
    redaction_module.redact_identifier = lambda value: "redacted"
    sys.modules.update({
        "app": types.ModuleType("app"),
        "app.core": types.ModuleType("app.core"),
        "app.core.log_redaction": redaction_module,
        "app.channels": types.ModuleType("app.channels"),
        "app.channels.base": base_module,
        "app.channels.lineworks.client": client_module,
    })

    spec = importlib.util.spec_from_file_location("lineworks_adapter", _ADAPTER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.LineWorksAdapter


def main() -> None:
    LineWorksAdapter = _load_adapter()
    body = b'{"type":"message"}'
    secret = "bot-secret"
    signature = base64.b64encode(
        hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    ).decode("utf-8")

    missing_secret = LineWorksAdapter(SimpleNamespace(bot_secret=None), 100)
    assert missing_secret.verify_signature(body, "") is False

    configured = LineWorksAdapter(SimpleNamespace(bot_secret=secret), 100)
    assert configured.verify_signature(body, signature) is True
    assert configured.verify_signature(body, "invalid") is False

    whitespace = {
        "type": "message",
        "source": {"userId": "u1"},
        "content": {"type": "text", "text": "   "},
    }
    assert configured.parse_inbound(whitespace) is None

    print("LINE WORKS signature checks passed")


if __name__ == "__main__":
    main()
