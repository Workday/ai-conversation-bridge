# Architecture

<p align="center"><sub>
  English |
  <a href="../i18n/zh-Hans/docs/architecture.md">简体中文</a> |
  <a href="../i18n/zh-Hant/docs/architecture.md">繁體中文</a> |
  <a href="../i18n/ja/docs/architecture.md">日本語</a> |
  <a href="../i18n/ko/docs/architecture.md">한국어</a>
</sub></p>

---

## Overview
<p align="center">
   <img width="900" height="490" alt="high level architecture" src="https://github.com/user-attachments/assets/cdd3bcc0-ece8-48ab-9631-0006513cb5a8" />
</p>

The AI Conversation Bridge is a reference architecture for connecting enterprise messaging platforms to Workday through AI-powered orchestration. It addresses four key challenges in the APJ region:

1. **Regulatory restrictions** — Chinese regulations block foreign-hosted LLMs
2. **Language/context gaps** — Enterprise LLMs don't handle customer-specific jargon well
3. **Super-app dominance** — Workers in China use WeChat, Japan uses LINE, Korea uses KakaoTalk
4. **Android unavailability** — Google Play Store is blocked in China

## What This Repo Is / Is Not

### What this repo is

- A reference implementation of the bridge pattern: chat adapter -> Flowise orchestration -> MCP tools -> Workday system of action.
- A development and demo environment with a mock MCP server so teams can prototype flows safely.
- A starting point for customers and partners to build production deployments in their own environments.

### What this repo is not

- Not a production-ready Workday MCP endpoint or substitute for Workday Agent Gateway.
- Not a complete multi-platform adapter pack in a single release.
- Not a managed runtime for Flowise or LLM hosting.

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          AI CONVERSATION BRIDGE                              │
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌───────────┐   │
│  │ Chat Platform  │  │     Chat       │  │    Flowise     │  │    MCP    │   │
│  │  (External)    │─▶│   Connector    │─▶│  (The Core)    │─▶│  Server   │   │
│  │                │◀─│                │◀─│                │◀─│ (Workday) │   │
│  └────────────────┘  └────────────────┘  └────────────────┘  └───────────┘   │
│                                                                              │
│  LINE WORKS          Webhook adapter     LLM orchestration    Tool execution │
│  WeChat              Message routing     Intent recognition   Workday APIs   │
│  KakaoTalk           Response delivery   Jargon translation   Mock data(dev) │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Chat Connector (`chat-connector/`)

A thin, stateless Flask application that:

- Receives webhooks from messaging platforms
- Extracts the user's message and identity
- Forwards the message to Flowise
- Sends the AI response back to the user

The connector has **no business logic** — it's purely an adapter. Adding a new chat platform means adding a new service file, not changing the AI pipeline.

Because it receives webhooks from external messaging platforms, the chat connector **must be deployed to a public-facing environment** with an HTTPS endpoint. Google Cloud Run is the reference example, but any container platform that provides a public URL works (AWS App Runner, Azure Container Apps, Alibaba Cloud Elastic Container Instance, Tencent Kubernetes Engine, etc.).

**Runtime:** Python / Gunicorn / Cloud Run (or equivalent public-facing container platform)

### Flowise (`flowise/`)

The actual "bridge" — a Flowise flow that:

- Receives messages from the chat connector
- Processes them through a customer-chosen LLM
- Recognizes intent and translates jargon
- Calls Workday tools via MCP
- Returns formatted responses

Flowise is managed by the customer in their own cloud environment. This project provides flow templates, not a Flowise runtime. If self-hosting Flowise, it must be deployed to **public-facing infrastructure** so that the chat connector can reach its prediction API.

**Runtime:** Customer-managed Flowise instance (cloud or self-hosted on public-facing infrastructure)

### MCP Server (`mcp-demo-server/`)

This project includes a demo MCP server with mock Workday tools and sample data for development and testing. Like the chat connector, the demo server should be **deployed to a cloud environment** (e.g., Google Cloud Run, Alibaba Cloud Elastic Container Instance, Tencent Kubernetes Engine) so that Flowise can reach it. Any container platform with a public URL works.

The demo server has **no authentication** and is not suitable for production use. In production, replace it with **Workday's official MCP endpoints** via Agent Gateway, which provides enterprise-grade security (OAuth 2.1, mTLS, audit logging, network policies). Update the MCP URL in your Flowise flow to point to the Agent Gateway URL instead.

**Runtime:** Python / FastMCP / Cloud Run (demo) or Workday Agent Gateway (prod)

## Request Flow

```
1. User sends "How many vacation days do I have?" in LINE WORKS
   │
2. LINE WORKS POSTs webhook to Chat Connector (/callback)
   │
3. Chat Connector extracts message + userId, calls Flowise prediction API
   │
4. Flowise LLM recognizes intent: get_current_user_time_off_balance
   │
5. Flowise MCP client calls MCP server → get_current_user_time_off_balance()
   │
6. MCP server returns: { vacation: { available: 12, used: 3 } }
   │
7. Flowise LLM formats response: "You have 12 vacation days remaining (3 used of 15 total)"
   │
8. Chat Connector receives response, sends it back to user via LINE WORKS API
```

## Key Design Principles

### Clean Separation of Concerns

- **Workday** stays the secure "system of action" via MCP
- **Customer** controls the AI layer (their own LLM) and messaging/UI
- **The Bridge** (Flowise) connects the two without storing sensitive data

### Data Sovereignty

The customer's LLM runs in their own environment. Messages are processed through their infrastructure. The Bridge respects regulatory requirements by design.

### Platform Agnostic

The chat connector pattern is repeatable for any messaging platform. The Flowise flow doesn't know or care which chat app the user is on.

### Production Hardening

This reference architecture implements baseline security (webhook signature verification, input limits, response validation). For production deployments, see the [Enterprise Hardening Guide](enterprise-guide.md) for additional recommendations on rate limiting, PII handling, retry logic, identity mapping, observability, and infrastructure choices (official Workday MCP servers, Flowise Cloud Enterprise).
