"""Helpers for keeping personal identifiers out of application logs."""

import hashlib


def redact_identifier(value: str | None) -> str:
    """Return a short, stable, non-reversible token for a user identifier.

    The same input always maps to the same token, so log lines for one user can
    still be correlated without the raw platform ID reaching the log backend.
    """
    if not value:
        return "unknown"
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return f"user-{digest[:8]}"
