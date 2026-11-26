"""Check documented MCP auth-header formats without network requests.

Run: PYTHONPATH=. python tests/check_mcp_auth_headers.py
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from app.orchestration.langgraph.tools.mcp import load_mcp_tools
from langchain_core.tools import StructuredTool


async def main() -> None:
    def synthetic_tool() -> str:
        """Return synthetic fixture data."""
        return "ok"

    tool = StructuredTool.from_function(synthetic_tool)
    tool.name = "get_current_user_info"
    connections: list[dict] = []

    class RecordingClient:
        def __init__(self, servers: dict) -> None:
            connections.append(servers)

        async def get_tools(self) -> list:
            return [tool]

    cases = [
        (None, {}),
        ("   ", {}),
        ("  synthetic-token  ", {"Authorization": "Bearer synthetic-token"}),
        ("Basic YTpi", {"Authorization": "Basic YTpi"}),
        ('Digest uri="/a:b"', {"Authorization": 'Digest uri="/a:b"'}),
        ("X-API-Key: one:two", {"X-API-Key": "one:two"}),
        ("", {}),
        ("authorization-token", {"Authorization": "Bearer authorization-token"}),
        ("Authorization-token", {"Authorization": "Bearer Authorization-token"}),
        ("AUTHORIZATIONtoken", {"Authorization": "Bearer AUTHORIZATIONtoken"}),
        ("authorization", {"Authorization": "Bearer authorization"}),
        ("authorization: Bearer synthetic-token", {"Authorization": "Bearer synthetic-token"}),
        ("Authorization : Bearer synthetic-token", {"Authorization": "Bearer synthetic-token"}),
        ("synthetic-token", {"Authorization": "Bearer synthetic-token"}),
        ("Bearer synthetic-token", {"Authorization": "Bearer synthetic-token"}),
        ("bearer synthetic-token", {"Authorization": "bearer synthetic-token"}),
        ("Authorization: Bearer synthetic-token", {"Authorization": "Bearer synthetic-token"}),
        ("Authorization: Basic synthetic", {"Authorization": "Basic synthetic"}),
        ("X-API-Key: synthetic-token", {"X-API-Key": "synthetic-token"}),
        ("Basic synthetic", {"Authorization": "Basic synthetic"}),
        ("Digest synthetic", {"Authorization": "Digest synthetic"}),
    ]
    failures = []
    with patch("app.orchestration.langgraph.tools.mcp.MultiServerMCPClient", RecordingClient):
        for value, expected in cases:
            returned = await load_mcp_tools("https://mcp.example.invalid/mcp", value, tool.name)
            assert returned == [tool]
            connection = connections[-1]["workday"]
            assert connection["url"] == "https://mcp.example.invalid/mcp"
            assert connection["transport"] == "streamable_http"
            if connection.get("headers", {}) != expected:
                failures.append((value, connection.get("headers", {}), expected))
    assert not failures, failures
    print(f"mcp auth header checks passed ({len(cases)} formats)")


if __name__ == "__main__":
    asyncio.run(main())
