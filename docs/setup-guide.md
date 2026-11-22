# Setup Guide

<p align="center"><sub>
  English |
  简体中文 |
  繁體中文 |
  日本語 |
  한국어
  <br>
  Translations of this guide are in progress. <a href="../CONTRIBUTING.md#translations">Help translate</a>.
</sub></p>

---

> **Flowise sunset:** [Flowise](https://flowiseai.com/sunset) EOL date **31 August 2026**. This guide defaults to **LangGraph**. See [Deprecated Flowise path](#deprecated-flowise-path) only if you still self-host from the [archived repository](https://github.com/FlowiseAI/Flowise).

This guide walks through installing, configuring, and verifying the AI Conversation Bridge. Examples use Google Cloud Run; any platform that gives you a public HTTPS webhook URL works.

## Before you begin

- `git`, `gcloud`, and Docker (for local smoke tests)
- A GCP project with billing enabled and APIs: Cloud Run, Cloud Build, Artifact Registry
- An OpenRouter API key for the default path, or OpenAI credentials with `LLM_BASE_URL` and `LLM_MODEL` overrides
- Credentials for at least one supported chat platform: LINE WORKS, DingTalk, or Feishu

**Network boundaries:** only the bridge webhook must be publicly reachable. The MCP server only needs to be reachable from the bridge. Keep MCP and LLM endpoints private or authenticated when possible.

## Choose a path

| Path | Orchestrator | MCP required? |
| --- | --- | --- |
| **Default demo** | `langgraph` | Yes |
| **Webhook smoke test** | `direct_llm` | No |
| **Legacy compatibility** | `flowise` (deprecated) | Via Flowise, not bridge |

Set `ORCHESTRATOR` explicitly when migrating from v0.1.0. Legacy `AI_PROVIDER` / `CHAT_PROVIDER` still map when `ORCHESTRATOR` is unset.

Variable reference: [bridge-service/.env.example](../bridge-service/.env.example) (catalog of names; **not** read by Cloud Run).

## Local smoke test (optional)

`bridge-service/.env` is used **only** by Docker Compose — not by `gcloud run deploy`.

```bash
./scripts/setup.sh
# Edit bridge-service/.env:
#   ORCHESTRATOR=langgraph
#   LLM_API_KEY=...
#   MCP_SERVER_URL=http://mcp-demo-server:8080/mcp

docker compose up --build
curl -sS http://localhost:8080/
```

Compose is for build/log inspection. Chat webhooks still need a public URL in real use.

## Cloud Run: LangGraph (default)

### 1. Deploy both services

```bash
REGION=us-west1

# Demo MCP server (no secrets)
gcloud run deploy mcp-demo-server \
  --source mcp-demo-server \
  --region "$REGION" \
  --allow-unauthenticated

# Bridge — first revision only (LangGraph needs LLM_API_KEY + MCP_SERVER_URL to boot)
gcloud run deploy bridge-service \
  --source bridge-service \
  --region "$REGION" \
  --allow-unauthenticated \
  --max-instances=1 \
  --concurrency=8 \
  --set-env-vars "LLM_API_KEY=your-openrouter-key,MCP_SERVER_URL=https://<mcp-service-url>/mcp"
```

**Helper script** (derives `MCP_SERVER_URL` after MCP deploy):

```bash
LLM_API_KEY=your-openrouter-key ./scripts/deploy-cloud-run.sh "$REGION"
```

`--max-instances=1` keeps in-memory conversation state on one replica. `--concurrency=8` matches gunicorn `--threads 8` in the bridge Dockerfile.

**Defaults note:** unset `LLM_BASE_URL` / `LLM_MODEL` send requests to OpenRouter (`openrouter/free`). Set those in the Cloud Run console if you use OpenAI or another provider.

### 2. Add channel credentials

Use the Cloud Run console (**Variables & secrets**). You can also use `gcloud run services update --update-env-vars`.

Do **not** rerun the first deploy command with `--set-env-vars` — that replaces every env var and removes console edits.

For `LW_API_20_PRIVATEKEY`, prefer Secret Manager in the console or:

```bash
gcloud run services update bridge-service \
  --region "$REGION" \
  --update-secrets "LW_API_20_PRIVATEKEY=lw-private-key:latest"
```

### 3. Verify

**Bridge health:**

```bash
curl -sS "https://<bridge-service-url>/"
```

Expect `{"status":"ok","orchestrator":"langgraph",...}`.

**Startup logs:**

```bash
gcloud run services logs read bridge-service --region "$REGION" --limit 50 \
  | grep -E "LangGraph|MCP tools|startup failed"
```

Expect tool discovery logs and no `startup failed`.

Send one real chat message to confirm delivery.

### 4. Redeploy code only

After channel vars are in the console, push new bridge code without touching env:

```bash
gcloud run deploy bridge-service --source bridge-service --region "$REGION"
```

### 5. Connect a chat platform

- LINE WORKS: `<bridge-url>/lineworks/callback` (legacy `/callback` still works)
- DingTalk: `<bridge-url>/dingtalk/callback`
- Feishu: `<bridge-url>/feishu/callback`

### LangGraph configuration notes

- Leave `MCP_TOOL_ALLOWLIST` unset to use the built-in **reference allowlist** (includes mock read tools and `request_my_time_off`). It is not a security boundary.
- `LLM_MESSAGE_WINDOW` limits model input for each turn; the in-memory checkpointer can still retain full thread history.
- LangGraph fails startup if MCP is unreachable, an allowlisted tool name is missing, or zero tools remain.
- With `STATE_BACKEND=memory`, use `--max-instances=1` so conversation state does not fragment across replicas. `--concurrency=8` matches gunicorn `--threads 8`. `--min-instances=1` is optional (reduces cold starts, adds cost) and does not make memory durable across restarts.

## Direct LLM smoke test

Use this to verify webhooks before adding MCP:

```bash
ORCHESTRATOR=direct_llm
LLM_API_KEY=your-key
LLM_MODEL=openrouter/free
LLM_BASE_URL=https://openrouter.ai/api/v1
```

No `MCP_SERVER_URL` required.

## Channel setup

### LINE WORKS

1. Create a bot in the [LINE WORKS Developer Console](https://developers.worksmobile.com/).
2. Configure OAuth / service account credentials and map them to `LW_API_20_*` (see `.env.example` for names; set values in the Cloud Run console).
3. Set `LW_API_20_BOT_SECRET`; without it, callbacks are rejected with HTTP 401.
4. Set callback URL to `<bridge-url>/lineworks/callback`.

**Private keys:** paste directly, use literal `\n`, or store in Secret Manager. The bridge normalizes PEM formatting.

### DingTalk

Follow the HTTP robot setup in the developer console. Publish the app version so `senderStaffId` is included in webhooks.

`DINGTALK_ALLOWED_USERS` is a **sender filter**, not cryptographic authentication. The demo path has no inbound signature verification. Treat a public bridge URL as demo-only unless you add ingress controls.

### Feishu (Lark)

1. Create an app and enable bot + `im.message.receive_v1` event subscription.
2. Copy `FEISHU_VERIFICATION_TOKEN`, `FEISHU_APP_ID`, and `FEISHU_APP_SECRET` into the bridge **before** saving the callback URL.
3. Set callback URL to `<bridge-url>/feishu/callback`.
4. Leave Encrypt Key disabled unless you add decryption support.

Feishu retries quickly; the bridge deduplicates by `message_id` in-process.

## Production MCP migration

Moving from the demo server is not URL-only. Plan for:

1. Tool discovery on the target endpoint
2. Updating `MCP_TOOL_ALLOWLIST` and prompts for real tool names/schemas
3. Supported authentication (static header today; OAuth/mTLS may need more integration)
4. Per-chat-user Workday identity — demo uses one global `CURRENT_USER_WORKER_ID`
5. Disabling or gating write tools until authorization is verified

See [mcp-demo-server/README.md](../mcp-demo-server/README.md#production) and [Enterprise Hardening Guide](enterprise-guide.md).

## Cleanup

```bash
gcloud run services delete bridge-service --region "$REGION"
gcloud run services delete mcp-demo-server --region "$REGION"
```

`--min-instances=1` incurs idle cost if you set it in the console. Remove it for experiments.

## Deprecated Flowise path

Flowise EOL date: 31 August 2026 ([announcement](https://flowiseai.com/sunset)). Fork the [archived repository](https://github.com/FlowiseAI/Flowise) if you must continue self-hosting. Set `ORCHESTRATOR=flowise` and `FLOWISE_API_URL` on the bridge. See [flowise/README.md](../flowise/README.md).
