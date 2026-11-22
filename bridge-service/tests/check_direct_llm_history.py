"""Assert DirectLLMClient session history is bounded (LRU) across distinct users.

Run: PYTHONPATH=. python tests/check_direct_llm_history.py
"""

from __future__ import annotations

from app.orchestration.direct_llm.client import DEFAULT_MAX_SESSIONS, DirectLLMClient


def _client(max_sessions: int) -> DirectLLMClient:
    return DirectLLMClient("key", "model", "http://localhost/chat/completions", max_sessions=max_sessions)


def main() -> None:
    client = _client(3)
    for user in ("u1", "u2", "u3"):
        client._append_to_history(user, "user", f"hi {user}")
    assert list(client.chat_history) == ["u1", "u2", "u3"]

    # A fourth user evicts the least recently used session (u1).
    client._append_to_history("u4", "user", "hi u4")
    assert list(client.chat_history) == ["u2", "u3", "u4"], list(client.chat_history)

    # Touching a session marks it recently used, so the next eviction skips it.
    client._append_to_history("u2", "assistant", "still here")
    client._append_to_history("u5", "user", "hi u5")
    assert list(client.chat_history) == ["u4", "u2", "u5"], list(client.chat_history)

    # An evicted user simply starts a fresh history.
    client._append_to_history("u1", "user", "back again")
    assert client.chat_history["u1"] == [{"role": "user", "content": "back again"}]
    assert len(client.chat_history) == 3

    # The existing per-session message trim still applies.
    solo = _client(2)
    for i in range(solo.history_limit + 5):
        solo._append_to_history("u1", "user", f"m{i}")
    assert len(solo.chat_history["u1"]) == solo.history_limit
    assert solo.chat_history["u1"][-1]["content"] == f"m{solo.history_limit + 4}"

    # Default bound is applied when none is given.
    default = DirectLLMClient("key", "model", "http://localhost/chat/completions")
    assert default.max_sessions == DEFAULT_MAX_SESSIONS
    for i in range(DEFAULT_MAX_SESSIONS + 50):
        default._append_to_history(f"user-{i}", "user", "x")
    assert len(default.chat_history) == DEFAULT_MAX_SESSIONS

    print("direct llm history checks passed")


if __name__ == "__main__":
    main()
