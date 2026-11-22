"""Application configuration loaded from environment variables."""

import logging
import os

logger = logging.getLogger(__name__)


def _env(*names: str, default: str | None = None) -> str | None:
    """Return the first non-empty environment value among names, else default."""
    for name in names:
        value = os.environ.get(name)
        if value is not None and value != "":
            return value
    return default


class Config:
    """Centralized environment-backed settings for the bridge service."""

    # LINE WORKS API
    LW_CLIENT_ID = os.environ.get("LW_API_20_CLIENT_ID")
    LW_CLIENT_SECRET = os.environ.get("LW_API_20_CLIENT_SECRET")
    LW_SERVICE_ACCOUNT_ID = os.environ.get("LW_API_20_SERVICE_ACCOUNT_ID")
    LW_PRIVATE_KEY = os.environ.get("LW_API_20_PRIVATEKEY")
    LW_BOT_ID = os.environ.get("LW_API_20_BOT_ID")
    LW_BOT_SECRET = os.environ.get("LW_API_20_BOT_SECRET")

    BASE_API_URL = "https://www.worksapis.com/v1.0"
    BASE_AUTH_URL = "https://auth.worksmobile.com/oauth2/v2.0"

    # DingTalk HTTP robot callbacks
    DINGTALK_ALLOWED_USERS = os.environ.get("DINGTALK_ALLOWED_USERS", "")
    DINGTALK_ALLOW_ALL_USERS = os.environ.get("DINGTALK_ALLOW_ALL_USERS", "false").lower() == "true"
    DINGTALK_REQUIRE_MENTION = os.environ.get("DINGTALK_REQUIRE_MENTION", "true").lower() == "true"
    DINGTALK_GROUP_SESSIONS_PER_USER = (
        os.environ.get("DINGTALK_GROUP_SESSIONS_PER_USER", "true").lower() == "true"
    )

    # Feishu (Lark) Open Platform
    FEISHU_VERIFICATION_TOKEN = os.environ.get("FEISHU_VERIFICATION_TOKEN")
    FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID")
    FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET")

    # Orchestrator: flowise | langgraph | direct_llm
    # Legacy AI_PROVIDER / CHAT_PROVIDER: flowise | openrouter
    _orchestrator_raw = os.environ.get("ORCHESTRATOR")
    _legacy_provider = _env("AI_PROVIDER", "CHAT_PROVIDER")
    if _orchestrator_raw:
        ORCHESTRATOR = _orchestrator_raw.lower()
    elif _legacy_provider:
        _mapped = _legacy_provider.lower()
        if _mapped == "openrouter":
            ORCHESTRATOR = "direct_llm"
            logger.warning(
                "AI_PROVIDER/CHAT_PROVIDER=openrouter is deprecated; "
                "use ORCHESTRATOR=direct_llm instead."
            )
        else:
            ORCHESTRATOR = _mapped
            logger.warning(
                "AI_PROVIDER/CHAT_PROVIDER is deprecated; "
                "use ORCHESTRATOR=%s instead.",
                ORCHESTRATOR,
            )
    else:
        ORCHESTRATOR = "langgraph"

    # Kept for health JSON compatibility for one release.
    AI_PROVIDER = "openrouter" if ORCHESTRATOR == "direct_llm" else ORCHESTRATOR
    CHAT_PROVIDER = AI_PROVIDER

    # LLM settings (direct_llm and langgraph). OpenAI Chat Completions only.
    # LLM_BASE_URL is the API root (…/v1); clients POST …/chat/completions.
    # OPENROUTER_* remain fallbacks.
    LLM_API_KEY = _env("LLM_API_KEY", "OPENROUTER_API_KEY")
    LLM_MODEL = _env("LLM_MODEL", "OPENROUTER_MODEL", default="openrouter/free")
    LLM_BASE_URL = _env("LLM_BASE_URL", default="https://openrouter.ai/api/v1")
    LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
    # None when unset so LangGraph keeps the bundled Workday prompt.
    LLM_SYSTEM_PROMPT = _env("LLM_SYSTEM_PROMPT", "OPENROUTER_SYSTEM_PROMPT")
    LLM_REASONING_EFFORT = _env("LLM_REASONING_EFFORT", "OPENROUTER_REASONING_EFFORT")
    LLM_MESSAGE_WINDOW = int(_env("LLM_MESSAGE_WINDOW", default="20"))

    # Deprecated aliases still referenced by older docs/scripts.
    OPENROUTER_API_KEY = LLM_API_KEY
    OPENROUTER_MODEL = LLM_MODEL
    OPENROUTER_API_URL = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
    OPENROUTER_SYSTEM_PROMPT = LLM_SYSTEM_PROMPT
    OPENROUTER_REASONING_EFFORT = LLM_REASONING_EFFORT

    # Flowise API (primary external orchestrator)
    FLOWISE_API_URL = os.environ.get("FLOWISE_API_URL")
    FLOWISE_API_KEY = os.environ.get("FLOWISE_API_KEY")
    FLOWISE_TIMEOUT = int(os.environ.get("FLOWISE_TIMEOUT", 120))

    # LangGraph state / MCP (Phase 4)
    STATE_BACKEND = os.environ.get("STATE_BACKEND", "memory").lower()
    MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL")
    MCP_AUTH_HEADER = os.environ.get("MCP_AUTH_HEADER")
    # None means use the built-in reference allowlist; "*" explicitly allows all
    # tools discovered from the MCP server.
    MCP_TOOL_ALLOWLIST = os.environ.get("MCP_TOOL_ALLOWLIST")
    ORCHESTRATOR_TIMEOUT = int(os.environ.get("ORCHESTRATOR_TIMEOUT", "240"))

    # App
    PORT = int(os.environ.get('PORT', 8080))
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

    # Security
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 1 * 1024 * 1024))  # 1 MB
    MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', 2000))
    # When true, replies containing hedging language ("I think", "probably", ...)
    # are replaced with the safe fallback instead of only being logged.
    BLOCK_HEDGED_RESPONSES = (
        os.environ.get('BLOCK_HEDGED_RESPONSES', 'false').lower() == 'true'
    )

    @classmethod
    def validate_for_orchestrator(cls) -> None:
        """Fail process startup when required settings for ORCHESTRATOR are missing."""
        name = cls.ORCHESTRATOR
        if name == "flowise":
            if not cls.FLOWISE_API_URL:
                raise SystemExit(
                    "ORCHESTRATOR=flowise requires FLOWISE_API_URL to be set."
                )
        elif name == "direct_llm":
            if not cls.LLM_API_KEY:
                raise SystemExit(
                    "ORCHESTRATOR=direct_llm requires LLM_API_KEY "
                    "(or legacy OPENROUTER_API_KEY) to be set."
                )
        elif name == "langgraph":
            missing = []
            if not cls.LLM_API_KEY:
                missing.append("LLM_API_KEY (or OPENROUTER_API_KEY)")
            if not cls.MCP_SERVER_URL:
                missing.append("MCP_SERVER_URL")
            if missing:
                raise SystemExit(
                    "ORCHESTRATOR=langgraph requires "
                    + ", ".join(missing)
                    + " to be set."
                )
            if cls.LLM_MESSAGE_WINDOW <= 0:
                raise SystemExit("ORCHESTRATOR=langgraph requires LLM_MESSAGE_WINDOW > 0.")
            try:
                from app.orchestration.langgraph.tools.mcp import parse_mcp_tool_allowlist

                parse_mcp_tool_allowlist(cls.MCP_TOOL_ALLOWLIST)
            except ValueError as e:
                raise SystemExit(f"Invalid MCP_TOOL_ALLOWLIST: {e}") from e
        else:
            raise SystemExit(
                f"Unknown ORCHESTRATOR={name!r}. "
                "Expected one of: flowise, langgraph, direct_llm."
            )
