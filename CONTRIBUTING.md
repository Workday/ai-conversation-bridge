# Contributing to AI Conversation Bridge

<p align="center"><sub>
  English |
  <a href="i18n/zh-Hans/CONTRIBUTING.md">简体中文</a> |
  <a href="i18n/zh-Hant/CONTRIBUTING.md">繁體中文</a> |
  <a href="i18n/ja/CONTRIBUTING.md">日本語</a> |
  <a href="i18n/ko/CONTRIBUTING.md">한국어</a>
</sub></p>

---

This project is a **reference architecture** — most teams will fork and customize it for their own deployments. If you'd like to contribute improvements back upstream (bug fixes, new chat platform adapters, documentation, new demo MCP tools, new Flowise flow templates), this guide explains how.

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## What We Welcome

| Contribution type | Process |
|-------------------|---------|
| Bug fixes | Open a PR |
| Documentation improvements | Open a PR |
| New chat platform adapters (e.g., WeChat, KakaoTalk) | Open a PR |
| New demo MCP tools (with mock data) | Open a PR |
| New Flowise flow templates | Open a PR |
| Architectural or framework changes | Open an issue first to discuss |

## License

This project is licensed under the [Apache License 2.0](LICENSE). By submitting a pull request, you agree that your contribution is licensed under the same terms and that you have the right to grant that license.

## Development Setup

All components are designed for **cloud deployment** — chat platform webhooks and Flowise require public HTTPS endpoints. See the [Setup Guide](docs/setup-guide.md) for full deployment instructions.

For local builds and verification:

```bash
./scripts/setup.sh          # create .env files from templates
docker compose build         # verify Dockerfiles
docker compose up --build    # run locally for log inspection / MCP testing
```

> **Tip:** To test the chat connector without Flowise, set `CHAT_PROVIDER=openrouter` and provide an `OPENROUTER_API_KEY`. This connects the webhook flow directly to an LLM.

## Making Changes

Follow existing patterns in each component. The key conventions:

- **Chat connector** (`chat-connector/app/`) — Config in `config.py`, routes in `routes.py`, one service file per platform/provider in `services/`. New chat platform adapters should follow `lineworks.py` as a reference. Update `.env.example` with any new required variables.

- **Flowise flows** (`flowise/flows/`) — Export flows as JSON from Flowise. Include screenshots in `flowise/screenshots/` and document the flow's purpose and required configuration in `flowise/README.md`. Ensure new flows work with the demo MCP server.

- **MCP server** (`mcp-demo-server/`) — New tools go in `main.py` with type hints and docstrings. Add corresponding mock data as JSON in `mock_data/`.

## Pull Request Process

1. **Open an issue first** for non-trivial changes so we can align on approach
2. **Verify containers build** — `docker compose build`
3. **Test your changes** — deploy to a cloud environment for end-to-end verification
4. **Update documentation** if you're changing behavior
5. **Don't commit secrets** — no `.env` files, API keys, or credentials
6. **Write a clear PR description** — the [PR template](.github/PULL_REQUEST_TEMPLATE.md) will guide you

## Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting (configured in `pyproject.toml`). Run `ruff check` before submitting. Use type hints and docstrings for public functions. Don't add dependencies without discussion.

## Reporting Issues

- **Bugs:** Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- **Feature requests:** Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- **Security vulnerabilities:** Do NOT open a public issue — see [SECURITY.md](SECURITY.md)
