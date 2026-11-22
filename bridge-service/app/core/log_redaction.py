"""Helpers for keeping personal identifiers out of application logs."""

import hashlib
import logging
import re

# LINE WORKS puts the recipient in the request path: .../bots/<bot>/users/<user id>/messages
_USER_PATH = re.compile(r"(/users/)([^/?#\s]+)")


def redact_identifier(value: str | None) -> str:
    """Return a short, stable, non-reversible token for a user identifier.

    The same input always maps to the same token, so log lines for one user can
    still be correlated without the raw platform ID reaching the log backend.
    """
    if not value:
        return "unknown"
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return f"user-{digest[:16]}"


def redact_user_paths(text: str) -> str:
    """Replace the user id in any ``/users/<id>`` path segment with its redacted token."""
    return _USER_PATH.sub(lambda m: m.group(1) + redact_identifier(m.group(2)), text)


class UserPathRedactionFilter(logging.Filter):
    """Logging filter that redacts ``/users/<id>`` in a record's rendered message.

    httpx logs every request URL at INFO ("HTTP Request: POST https://...") and the
    LINE WORKS send URL carries the raw user id, so this is attached to the
    ``httpx`` logger.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        redacted = redact_user_paths(message)
        if redacted != message:
            record.msg, record.args = redacted, ()
        return True


def install_httpx_redaction() -> None:
    """Attach the filter to the ``httpx`` logger once."""
    log = logging.getLogger("httpx")
    if not any(isinstance(f, UserPathRedactionFilter) for f in log.filters):
        log.addFilter(UserPathRedactionFilter())
