# Demo MCP Server

<p align="center"><sub>
  English |
  <a href="../i18n/zh-Hans/mcp-demo-server/README.md">简体中文</a> |
  <a href="../i18n/zh-Hant/mcp-demo-server/README.md">繁體中文</a> |
  <a href="../i18n/ja/mcp-demo-server/README.md">日本語</a> |
  <a href="../i18n/ko/mcp-demo-server/README.md">한국어</a>
</sub></p>

---

A lightweight MCP server with mock Workday tools for development and demo purposes. It provides a handful of common Workday actions — time-off requests, worker lookups, and employee data — backed by static sample data instead of a real Workday tenant.

**This is not a production MCP server.** In production, point the bridge's LangGraph orchestrator (`MCP_SERVER_URL`) at official Workday MCP server endpoints via Agent Gateway, which provides authenticated access to the full Workday API surface.

## What's Included

| Tool                                | Description                                          |
| ----------------------------------- | ---------------------------------------------------- |
| `find_employee_id_by_name`          | Look up an employee's worker ID by name              |
| `get_current_user_info`             | Get the current user's profile                       |
| `get_current_user_payslips`         | Get current user's payslip or history by period      |
| `get_current_user_time_off_balance` | Get the current user's leave balances                |
| `get_current_user_time_off_history` | Get the current user's leave request history         |
| `get_time_off_balance`              | Get leave balances for any worker by ID              |
| `get_direct_reports`                | List direct reports for a manager                    |
| `get_more_employee_data`            | Get extended employee data                           |
| `get_my_time_off_eligibility`       | Check which leave types the current user can request |
| `get_payslip_by_worker_id`          | Get payslip for any worker by ID and period          |
| `get_personal_information`          | Get personal info (address, emergency contact)       |
| `get_today_date_and_day_of_week`    | Get the current date and time                        |
| `request_my_time_off`               | Submit a time-off request for the current user       |

The mock data in `mock_data/` includes five sample workers across Shanghai, Beijing, Tokyo, and Seoul with localized names and currencies (CNY, JPY, KRW).

## What's NOT Included

This demo server intentionally covers only a small slice of what Workday exposes. It does not include:

- Benefits enrollment
- Expense reports
- Recruiting / job applications
- Learning and development
- Compensation changes
- Org chart navigation
- Approvals and workflow actions
- Any real authentication or authorization

For the full set of Workday capabilities, use the official Workday MCP server endpoints.

## Running

Deploy the demo MCP server so the bridge service can reach it (private network preferred; public demo deploys are common for quick tests). See the [Setup Guide](../docs/setup-guide.md) for deployment instructions.

The server uses [FastMCP](https://gofastmcp.com/) with streamable HTTP transport by default, listening at the `/mcp` path.

## Connecting from the bridge

Set `MCP_SERVER_URL` on the bridge service to your deployed MCP server's URL **including** `/mcp`:

- **Cloud-hosted:** `https://mcp-demo-server-abc123.us-west1.run.app/mcp`

LangGraph discovers tools at bridge startup and filters them through the reference allowlist (or `MCP_TOOL_ALLOWLIST`).

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `streamable-http` | Transport protocol (`streamable-http` for HTTP, `stdio` for local) |
| `MCP_HOST` | `0.0.0.0` | Host to bind to |
| `MCP_PORT` | `8080` | Port to listen on |
| `MCP_PATH` | `/mcp` | URL path for the streamable HTTP endpoint |
| `PORT` | `8080` | Port to listen on (Cloud Run sets this automatically; takes precedence over `MCP_PORT`) |
| `CURRENT_USER_WORKER_ID` | `WK001` | Worker ID for the simulated "current user" — all `get_current_user_*` tools return data for this worker |

## Adding Tools

To add a new mock tool, add a function decorated with `@mcp.tool()` in `main.py` and create any supporting data in `mock_data/`. Follow the existing patterns — type hints and docstrings are used by MCP clients to understand the tool's schema.

## Production

Replace this demo server with official Workday MCP server endpoints via Agent Gateway. **This is not a URL swap.** Plan for:

1. Tool discovery on the production endpoint
2. Updating `MCP_TOOL_ALLOWLIST` and prompts for real tool names/schemas
3. Authentication (OAuth 2.1 / mTLS via Agent Gateway; `MCP_AUTH_HEADER` for static tokens today)
4. Per-chat-user Workday identity — demo uses one global `CURRENT_USER_WORKER_ID`
5. Disabling or gating write tools until authorization is verified

The tool names and schemas in this demo are illustrative — the real Workday MCP server has its own definitions, authentication requirements, and data formats.

### Production Security

This demo server has **no authentication or authorization**. Production MCP server deployments require significantly more security, including:

- **OAuth 2.1 / mTLS** — Authenticate clients connecting to the MCP server. Workday Agent Gateway handles this for official endpoints.
- **API keys or bearer tokens** — Gate access to specific tools and data. FastMCP supports bearer token auth out of the box for prototyping.
- **Network policies** — Restrict which services can reach the MCP server (e.g., only the bridge service).
- **Audit logging** — Track who called which tools and when.
- **Data encryption** — Ensure all communication is over HTTPS/TLS in transit, and sensitive data is encrypted at rest.

Consult your organization's security team and Workday's Agent Gateway documentation for production authentication requirements.
