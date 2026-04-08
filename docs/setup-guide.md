# Setup Guide

<p align="center"><sub>
  English |
  <a href="../i18n/zh-Hans/docs/setup-guide.md">简体中文</a> |
  <a href="../i18n/zh-Hant/docs/setup-guide.md">繁體中文</a> |
  <a href="../i18n/ja/docs/setup-guide.md">日本語</a> |
  <a href="../i18n/ko/docs/setup-guide.md">한국어</a>
</sub></p>

---

This guide walks through setting up each component of the AI Conversation Bridge.

> **Important:** All components must be deployed to **public-facing cloud environments** so they can communicate with each other and receive webhooks from external platforms. This guide uses Google Cloud Run as the example, but any container platform with a public HTTPS endpoint works (AWS App Runner, Azure Container Apps, Alibaba Cloud Elastic Container Instance, Tencent Kubernetes Engine, etc.).

## Prerequisites

- A container hosting platform with public URLs (e.g., [Google Cloud Run](https://cloud.google.com/run))
- A Flowise instance ([cloud](https://flowiseai.com/) or [self-hosted](#self-hosting-flowise) on public-facing infrastructure)
- LINE WORKS Developer Console access (for bot credentials)

## 1. Demo MCP Server

The demo MCP server provides mock Workday tools for development and testing. Like the chat connector, it should be **deployed to a cloud environment** (e.g., Google Cloud Run) so that your Flowise instance can reach it. If you use a different provider (AWS App Runner, Azure Container Apps, Alibaba Cloud Elastic Container Instance, Tencent Kubernetes Engine, etc.), adapt the deployment commands accordingly.

> **Production note:** The demo MCP server is for development only and has no authentication. In production, configure your Flowise flow's MCP client node to point to **Workday's official MCP endpoints** via Agent Gateway, which provides OAuth 2.1, mTLS, and other enterprise security controls. See the [Production Security](../mcp-demo-server/README.md#production-security) section for details.

### Deploy to Cloud Run

```bash
gcloud run deploy mcp-demo-server \
  --source mcp-demo-server
```

After deployment, Cloud Run provides a public URL (e.g., `https://mcp-demo-server-abc123.us-west1.run.app`). Use this URL when configuring the Flowise MCP client node.

### Verify

The MCP server exposes tools via streamable HTTP transport at the `/mcp` path. You can connect to it from any MCP client (Flowise, Claude Desktop, etc.) at your deployed URL (e.g., `https://mcp-demo-server-abc123.us-west1.run.app/mcp`).

## 2. Flowise Flow

### Import the Flow

1. Open your Flowise instance
2. Navigate to **Agent Flows** → **Add New**
3. Click **Settings** (⚙️) → **Load Agentflow**
4. Select `flowise/flows/workday-mcp-agent.json`

### Configure the Agent Node

After importing, click the **AI Bridge Agent** node and configure:

1. **Model** — The flow defaults to OpenRouter with the free `z-ai/glm-4.5-air:free` model (Z.ai GLM, a China-based LLM). Add an OpenRouter credential in Flowise, or switch to any other provider with your own API key. Good choices for APJ include Z.ai GLM, Qwen/Alibaba (Tongyi Qianwen), and DeepSeek for China-hosted deployments, or OpenAI, Anthropic, and Gemini elsewhere.
2. **Custom MCP Tool** — Update the MCP server URL in the tool configuration:
   - **Demo:** Your deployed demo MCP server URL + `/mcp` (e.g., `https://mcp-demo-server-abc123.us-west1.run.app/mcp`). For the demo server, you can omit the `Authorization` header.
   - **Production:** Your Workday Agent Gateway URL (replace the demo server with Workday's official MCP endpoints, which require proper authentication)

### Get the Prediction URL

1. Click the flow's **API Endpoint** button
2. Copy the prediction URL (e.g., `https://your-flowise.com/api/v1/prediction/<flow-id>`)
3. You'll need this for the chat connector configuration

## 3. Chat Connector

The chat connector receives webhooks from messaging platforms, so it **must be deployed to a public-facing environment** with an HTTPS URL. This guide uses Google Cloud Run as the example. If you use a different provider (AWS App Runner, Azure Container Apps, Alibaba Cloud Elastic Container Instance, Tencent Kubernetes Engine, etc.), adapt the deployment commands accordingly.

### Configuration

Prepare your environment variables. You can use `chat-connector/.env.example` as a reference:

```bash
# Point to your Flowise flow
CHAT_PROVIDER=flowise
FLOWISE_API_URL=https://your-flowise.com/api/v1/prediction/<flow-id>
FLOWISE_API_KEY=your-flowise-api-key

# LINE WORKS bot credentials
LW_API_20_CLIENT_ID=your-client-id
LW_API_20_CLIENT_SECRET=your-client-secret
LW_API_20_SERVICE_ACCOUNT_ID=your-service-account-id
LW_API_20_PRIVATEKEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
LW_API_20_BOT_ID=your-bot-id
LW_API_20_BOT_SECRET=your-bot-secret
```

> **Security:** `LW_API_20_BOT_SECRET` enables webhook signature verification — the connector rejects any callback whose `X-WORKS-Signature` header doesn't match. You can find your Bot Secret in the LINE WORKS Developer Console under your bot's details. If omitted, signature verification is skipped with a warning (acceptable for local development, **not for production**).

> **Note on private keys:** When setting `LW_API_20_PRIVATEKEY` in your container platform, newline handling varies. You can paste the key directly (the connector normalizes the format automatically), use literal `\n` characters, or store the key in a secrets manager (recommended). See [Private Key Formatting](#private-key-formatting) below.

### Deploy to Cloud Run

```bash
gcloud run deploy chat-connector \
  --source chat-connector
```

> **Important:** Don't forget to set your environment variables in the Cloud Run console after deploying! You will need to configure your AI provider (like `CHAT_PROVIDER` and `FLOWISE_API_URL`) as well as your LINE WORKS bot credentials. See `chat-connector/.env.example` for the full list of required variables.

After deployment, Cloud Run provides a public URL (e.g., `https://chat-connector-abc123.us-west1.run.app`). You'll use this as your webhook URL.

For sensitive values like `LW_API_20_PRIVATEKEY`, consider using [Google Secret Manager](https://cloud.google.com/run/docs/configuring/secrets) instead of plain environment variables:

```bash
gcloud run deploy chat-connector \
  --source . \
  --set-env-vars "CHAT_PROVIDER=flowise,FLOWISE_API_URL=..." \
  --set-secrets "LW_API_20_PRIVATEKEY=lw-private-key:latest"
```

### LINE WORKS Bot Setup

1. Go to the [LINE WORKS Developer Console](https://developers.worksmobile.com/)
2. Create a Bot
3. Set the callback URL to your deployed chat connector's public URL + `/callback` (e.g., `https://chat-connector-abc123.us-west1.run.app/callback`)
4. Set the environment variables on your container platform with the bot credentials

### Quick Test with OpenRouter

If you want to test the chat connector without Flowise:

```bash
CHAT_PROVIDER=openrouter
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=z-ai/glm-4.5-air:free
```

This connects LINE WORKS directly to an LLM via OpenRouter — useful for verifying the webhook flow works before adding Flowise orchestration.

### Private Key Formatting

Container platforms handle multi-line environment variables differently. The chat connector automatically normalizes the PEM private key, so all of these approaches work:

- **Paste directly** in the Cloud Run console or equivalent — newlines may become spaces, but the connector handles this
- **Use literal `\n`** when setting via CLI — e.g., `-----BEGIN PRIVATE KEY-----\nMIIEvQI...\n-----END PRIVATE KEY-----`
- **Use a secrets manager** (recommended) — stores the key with exact formatting preserved

### Scaling

The chat connector runs Gunicorn with a single worker process, meaning each container instance handles one request at a time. To support concurrent users, configure your Cloud Run (or equivalent container platform) auto-scaling settings to add instances as traffic increases. Key settings to consider:

- **Max instances** — controls cost by capping how many containers can run simultaneously
- **Concurrency** — set to 1 for the simplest model (one request per instance), or increase if you add Gunicorn threads
- **Min instances** — set to 1 or more to avoid cold starts for latency-sensitive environments

## Self-Hosting Flowise

If you prefer to host your own Flowise instance instead of using [Flowise Cloud](https://flowiseai.com/), it must be deployed to **public-facing infrastructure** so that the chat connector can reach its prediction API. Deploy Flowise to Cloud Run, Alibaba Cloud Elastic Container Instance, Tencent Kubernetes Engine, a VM with a public IP, or any platform that provides an HTTPS endpoint. See the [Flowise self-hosting documentation](https://docs.flowiseai.com/configuration/deployment) for deployment options.
