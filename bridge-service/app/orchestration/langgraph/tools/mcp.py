"""MCP tool discovery and allowlist filtering for the LangGraph orchestrator."""

from __future__ import annotations

import logging

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)

# Default authoritative allowlist from flowise/flows/workday-mcp-agent.json mcpActions.
# A tool the server exposes but this list omits must not reach the model unless
# MCP_TOOL_ALLOWLIST=* is explicitly configured.
DEFAULT_MCP_TOOL_ALLOWLIST = frozenset({
    "find_employee_id_by_name",
    "get_current_user_info",
    "get_current_user_payslips",
    "get_current_user_time_off_balance",
    "get_current_user_time_off_history",
    "get_direct_reports",
    "get_more_employee_data",
    "get_my_time_off_eligibility",
    "get_payslip_by_worker_id",
    "get_personal_information",
    "get_today_date_and_day_of_week",
    "request_my_time_off",
    "get_time_off_balance",
})


def parse_mcp_tool_allowlist(value: str | None) -> frozenset[str] | None:
    """Resolve env syntax; return None only for an explicit "*" allow-all."""
    if value is None:
        return DEFAULT_MCP_TOOL_ALLOWLIST

    entries = [entry.strip() for entry in value.split(",")]
    if not value.strip():
        raise ValueError("must contain comma-separated tool names or '*' (leave unset for defaults)")
    if any(not entry for entry in entries):
        raise ValueError("must not contain empty tool names")
    if "*" in entries:
        if len(entries) != 1:
            raise ValueError("'*' must be the only value")
        return None
    return frozenset(entries)


def filter_mcp_tools(
    discovered: list[BaseTool],
    allowed_names: frozenset[str] | None,
) -> list[BaseTool]:
    """Keep allowlisted tools. Fail if names are missing or nothing remains."""
    discovered_names = [t.name for t in discovered]
    if allowed_names is None:
        logger.warning("MCP_TOOL_ALLOWLIST=* enabled; retaining all discovered tools")
        filtered = list(discovered)
        missing: list[str] = []
    else:
        filtered = [t for t in discovered if t.name in allowed_names]
        missing = sorted(allowed_names - set(discovered_names))
    retained = [t.name for t in filtered]
    omitted = sorted(set(discovered_names) - set(retained))

    logger.info("MCP tools discovered (%d): %s", len(discovered_names), discovered_names)
    logger.info("MCP tools retained after allowlist (%d): %s", len(retained), retained)
    if omitted:
        logger.info("MCP tools omitted by allowlist: %s", omitted)
    if missing:
        logger.error("MCP tools missing from server: %s", missing)
        raise ValueError("MCP server is missing allowlisted tools: " + ", ".join(missing))
    if not filtered:
        raise ValueError("MCP server returned no usable tools")
    return filtered


async def load_mcp_tools(
    server_url: str,
    auth_header: str | None = None,
    tool_allowlist: str | None = None,
) -> list[BaseTool]:
    """Discover MCP tools once, filter to the configured allowlist, and return LangChain tools."""
    allowed_names = parse_mcp_tool_allowlist(tool_allowlist)
    headers = {}
    if auth_header:
        # Accept either a full "Authorization: Bearer …" value or a raw token.
        if ":" in auth_header and not auth_header.lower().startswith("authorization"):
            # "Authorization: Bearer x" style already
            name, _, value = auth_header.partition(":")
            headers[name.strip()] = value.strip()
        elif auth_header.lower().startswith("bearer ") or auth_header.lower().startswith("authorization"):
            headers["Authorization"] = (
                auth_header.split(":", 1)[-1].strip()
                if auth_header.lower().startswith("authorization")
                else auth_header
            )
        else:
            headers["Authorization"] = auth_header

    connection: dict = {
        "transport": "streamable_http",
        "url": server_url,
    }
    if headers:
        connection["headers"] = headers

    client = MultiServerMCPClient({"workday": connection})
    discovered = await client.get_tools()
    return filter_mcp_tools(discovered, allowed_names)
