# Enterprise Hardening Guide

<p align="center"><sub>
  English |
  <a href="../i18n/zh-Hans/docs/enterprise-guide.md">简体中文</a> |
  <a href="../i18n/zh-Hant/docs/enterprise-guide.md">繁體中文</a> |
  <a href="../i18n/ja/docs/enterprise-guide.md">日本語</a> |
  <a href="../i18n/ko/docs/enterprise-guide.md">한국어</a>
</sub></p>

---

Recommendations for teams moving the AI Conversation Bridge from prototype to production. This guide covers what comes next.

> **Start here:** The two highest-leverage steps are infrastructure choices, not code changes.

## Production Infrastructure

### Use Official Workday MCP Servers

The `mcp-demo-server/` in this repo is a mock with static JSON data and no authentication. Production deployments should connect to **Workday's official MCP servers** (e.g., Workday Agent Gateway), which provide real data access, OAuth 2.1 / mTLS authentication, audit logging, and compliance controls. Update the MCP server URL in your Flowise flow's Custom MCP tool to point to the Agent Gateway endpoint.

### Use Flowise Cloud Enterprise

Self-hosting Flowise works for prototyping, but [Flowise Cloud Enterprise](https://flowiseai.com/) offers SSO, role-based access control, audit trails, encryption at rest, and SLA-backed uptime — a significantly stronger posture for regulated industries. For countries with stricter data residency requirements (e.g., China, certain ASEAN markets), self-hosting Flowise in-region remains a valid production approach.

---

## P1 — High Priority

### Log Sanitization

The chat connector logs user IDs and message metadata. In production, log output often flows to centralized systems where PII exposure creates compliance risk (GDPR, PIPL, etc.). Introduce a sanitization layer that redacts user identifiers and message content before they reach log output. Structured JSON logging makes this easier — log processors can redact specific fields rather than relying on pattern matching.

### Rate Limiting

The `/callback` endpoint is publicly accessible. Without rate limiting, a misconfigured webhook or abuse scenario can exhaust downstream quotas (Flowise, LLM provider, LINE WORKS). Add per-IP and per-user rate limits at the chat connector layer. For multi-instance deployments, back the rate limiter with a shared store (e.g., Redis) rather than in-memory counters.

### Model Selection and Temperature

The reference flow uses a free-tier model (`z-ai/glm-4.5-air:free`). Free-tier models have aggressive rate limits (often 10-20 RPM) that will cause failures under real load. Switch to a paid model with strong function-calling support. Set temperature to near-0 for tool-calling agents — higher temperatures introduce non-determinism in intent recognition and tool argument generation, leading to hallucinated parameters or skipped tool calls.

### Structured Output Schemas

Without output constraints, the LLM can return responses in unpredictable formats. Flowise supports structured output schemas on the Agent node that force the LLM to conform to a defined shape. Consider including a `data_source` field (tool result vs. general knowledge) so downstream consumers can detect when the LLM answered from its own knowledge rather than from a Workday tool.

### User-to-Worker Identity Mapping

The demo server uses a single `CURRENT_USER_WORKER_ID` for all requests. In production, each chat user must map to their own Workday worker identity. The recommended approach is Workday-side resolution — the Agent Gateway resolves identity via tokens. 

---

## P2 — Medium Priority

### Retry Logic with Backoff

Transient failures (network blips, 502/503 from Flowise, token refresh races) are inevitable. Add retry logic with exponential backoff to outbound HTTP calls in the chat connector. Avoid retrying on `429` responses — those indicate you need to address rate limits at the provider level, not mask them with retries.

### Correlation IDs and Structured Logging

When a user reports "the bot didn't respond," you need to trace a single request across the chat connector, Flowise, and MCP pipeline. Generate a request ID at the `/callback` entry point, propagate it as an HTTP header through downstream calls, and attach it to all log entries. Structured JSON logging (rather than plain text) makes these traces queryable in Cloud Run, CloudWatch, and similar platforms.

### Prompt Injection Defenses

Users (or attackers replaying webhook payloads) can craft messages that attempt to override the LLM's system prompt. Layer multiple defenses: harden the system prompt with explicit override-rejection instructions, wrap user input in delimiters so it's harder for injected text to escape context, and optionally screen for common injection phrases as a logging signal. 

---

## P3 — Nice to Have

### Observability (Tracing and Metrics)

Add distributed tracing and metrics across the chat connector, Flowise, and MCP pipeline. This enables end-to-end latency visibility, error rate alerting, and the ability to diagnose issues before users report them.

### Circuit Breakers

If Flowise is down or consistently erroring, a circuit breaker pattern lets the chat connector fail fast with a user-friendly message rather than waiting for timeouts on every request. After a cooldown period, the breaker allows a probe request to check if the service has recovered.

### Output Content Filtering

Even with tool-grounded responses, LLMs can surface sensitive data in edge cases (e.g., full ID numbers in a personal info response). Extend the existing response validator with PII pattern detection. For authorization-level filtering, the Workday Agent Gateway handles this natively — tool results are scoped to what the authenticated user is allowed to see, which is another reason to use official Workday MCP servers.