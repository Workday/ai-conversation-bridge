# Flowise Flow Templates

<p align="center"><sub>
  English |
  <a href="../i18n/zh-Hans/flowise/README.md">简体中文</a> |
  <a href="../i18n/zh-Hant/flowise/README.md">繁體中文</a> |
  <a href="../i18n/ja/flowise/README.md">日本語</a> |
  <a href="../i18n/ko/flowise/README.md">한국어</a>
</sub></p>

---

> **Deprecated:** [Flowise](https://flowiseai.com/sunset) EOL date **31 August 2026**. These templates remain for `ORCHESTRATOR=flowise` compatibility only. New work should use bundled LangGraph in `bridge-service/`. To continue with Flowise itself, fork the [archived repository](https://github.com/FlowiseAI/Flowise).

This folder contains exportable Flowise flow templates retained for the deprecated `ORCHESTRATOR=flowise` path.

## Prerequisites

- A running [Flowise](https://flowiseai.com/) instance (cloud or self-hosted)
- An API key for your LLM provider (e.g., OpenRouter, Z.ai, Qwen, OpenAI, Anthropic, or a locally-hosted model)
- Access to an MCP server (use the demo server in `../mcp-demo-server/` for development)

## Available Flows

### Workday MCP Agent (`flows/workday-mcp-agent.json`)

An Agent Flow that acts as a **Workday Intelligent Assistant** — it receives natural-language HR/Finance requests and executes them through MCP tools.

**Nodes:**

| Node | Type | Purpose |
|------|------|---------|
| **Start** | Start | Chat input entry point |
| **AI Bridge Agent** | Agent | LLM-powered agent with system prompt, tools, and conversation memory |

**Agent configuration:**

- **Model:** OpenRouter (`openrouter/free`) — OpenRouter's free model router, suitable for demos. Replace with any OpenRouter-supported model or switch to Qwen/DeepSeek/OpenAI/Anthropic/Gemini/etc.
- **Temperature:** 0.2 (low, for deterministic tool-calling behavior)
- **Memory:** Window-based (last 20 messages)
- **System prompt:** Enforces strict tool-first behavior — the agent must call MCP tools to execute actions and cannot simulate or mock responses.

> **Keep in sync with LangGraph:** The same role and directives live as plain text in
> `bridge-service/app/orchestration/langgraph/prompts.py`. When you edit the Flowise
> `agentMessages` prompt or the MCP tool allowlist, update the LangGraph copies too
> (and vice versa). LangGraph can narrow or explicitly override its default list with
> `MCP_TOOL_ALLOWLIST`; leave that variable unset when the bundled list should mirror
> this flow. LangGraph fails startup if an allowlisted name is missing from the MCP server.

**Tools:**

1. **RSS News** (`get_rss_news`) — HTTP GET tool for fetching RSS feeds (demo/testing)
2. **Workday MCP** — Custom MCP client with 13 Workday tools:

| MCP Tool | Description |
|----------|-------------|
| `find_employee_id_by_name` | Look up an employee's worker ID by name |
| `get_current_user_info` | Get the current user's profile |
| `get_current_user_payslips` | Get current user's payslip or history by period |
| `get_current_user_time_off_balance` | Get the current user's leave balances |
| `get_current_user_time_off_history` | Get the current user's leave request history |
| `get_direct_reports` | List direct reports for a manager |
| `get_more_employee_data` | Get extended employee data |
| `get_my_time_off_eligibility` | Check which leave types the current user can request |
| `get_payslip_by_worker_id` | Get payslip for any worker by ID and period |
| `get_personal_information` | Get personal info (address, emergency contact) |
| `get_today_date_and_day_of_week` | Get the current date and time |
| `request_my_time_off` | Submit a time-off request |
| `get_time_off_balance` | Get leave balances for any worker by ID |

## Importing a Flow

1. Open your Flowise instance
2. Go to **Agent Flows** → **Add New**
3. Click the **Settings** icon (⚙️) → **Load Agentflow**
4. Select `flows/workday-mcp-agent.json`
5. Configure the nodes (see below)

## Configuration

After importing, you'll need to configure two things:

### 1. LLM (Agent Model)

The flow defaults to **OpenRouter** with the free `openrouter/free` model router. To use it:
- Add an OpenRouter credential in Flowise with your API key
- Or switch the model to any other provider and add the corresponding credential. Good choices for APJ include Z.ai GLM, Qwen, and DeepSeek for China-hosted deployments, or OpenAI, Anthropic, and Gemini elsewhere.

### 2. MCP Server URL

In the **AI Bridge Agent** node, update the Custom MCP tool's server config:

- **Development:** Point to your deployed demo MCP server:
  ```json
  {
    "key": "wd-mcp-server",
    "url": "https://YOUR_MCP_SERVER_URL/mcp",
    "headers": {
      "Authorization": "Bearer YOUR_MCP_API_KEY"
    },
    "approvalPolicy": "always"
  }
  ```
  For the demo server (no auth required), omit the `headers` field:
  ```json
  {
    "key": "wd-mcp-server",
    "url": "http://mcp-demo-server:8080/mcp",
    "approvalPolicy": "always"
  }
  ```

- **Production:** Point to your Workday Agent Gateway MCP endpoint with proper credentials.

## Customization

This template is a starting point. You can extend it in Flowise to:

- Swap the LLM model for a region-appropriate option (e.g., a China-hosted model for Chinese workers)
- Add custom system prompts with company-specific jargon
- Connect additional MCP tool servers
- Add RAG nodes for company knowledge bases
- Configure different conversation memory strategies
- Add output parsers for rich message formatting
- Remove the RSS news tool (it's included for demo purposes only)
