"""Assert DirectLLMClient session history is bounded (LRU) across distinct users.

Run: PYTHONPATH=. python tests/check_direct_llm_history.py
"""

from __future__ import annotations

import asyncio

import httpx
from app.orchestration.base import OrchestrationRequest
from app.orchestration.direct_llm.client import DEFAULT_MAX_SESSIONS, DirectLLMClient


def _client(max_sessions: int) -> DirectLLMClient:
    return DirectLLMClient("key", "model", "http://localhost/chat/completions", max_sessions=max_sessions)


class GatedHTTP:
    """Stands in for httpx.AsyncClient; a request whose message is in ``gates`` waits."""

    def __init__(self):
        self.gates: dict[str, asyncio.Event] = {}

    async def post(self, url, headers=None, json=None):
        text = json["messages"][-1]["content"]
        if text in self.gates:
            await self.gates[text].wait()
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": f"reply to {text}"}}]},
            request=httpx.Request("POST", url),
        )


async def _late_reply_after_eviction() -> None:
    client = _client(1)
    client._client = GatedHTTP()
    client._client.gates["a1"] = gate = asyncio.Event()

    def ask(session, text):
        return client.invoke(OrchestrationRequest(message=text, session_id=session))

    a = asyncio.create_task(ask("A", "a1"))
    await asyncio.sleep(0)                       # A is now waiting on the upstream call
    assert (await ask("B", "b1")).text == "reply to b1"   # B evicts A
    assert list(client.chat_history) == ["B"]
    gate.set()
    assert (await a).text == "reply to a1"       # A still gets its answer...
    assert list(client.chat_history) == ["B"], client.chat_history  # ...but is not recreated

    # Evicted, then restarted before the late reply lands: the fresh history stays clean.
    client._client.gates["a2"] = gate2 = asyncio.Event()
    a = asyncio.create_task(ask("A", "a2"))
    await asyncio.sleep(0)
    await ask("B", "b2")                         # evicts A
    await ask("A", "a3")                         # A restarts
    gate2.set()
    await a
    assert client.chat_history["A"] == [
        {"role": "user", "content": "a3"},
        {"role": "assistant", "content": "reply to a3"},
    ], client.chat_history["A"]

    # A normal round trip records both turns, also past the per-session trim.
    solo = _client(5)
    solo._client = GatedHTTP()
    for i in range(solo.history_limit):
        await solo.invoke(OrchestrationRequest(message=f"q{i}", session_id="u"))
    assert len(solo.chat_history["u"]) == solo.history_limit
    assert solo.chat_history["u"][-1] == {"role": "assistant", "content": f"reply to q{solo.history_limit - 1}"}


def main() -> None:
    for bad in (0, -1, 1.5, "10", True, None):
        try:
            _client(bad)
            raise AssertionError(f"max_sessions={bad!r} should be rejected")
        except ValueError:
            pass

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

    asyncio.run(_late_reply_after_eviction())

    print("direct llm history checks passed")


if __name__ == "__main__":
    main()
