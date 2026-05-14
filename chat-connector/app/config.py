import os


class Config:
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

    # AI Provider: "flowise" (recommended) or "openrouter" (demo/experiment).
    # CHAT_PROVIDER is kept as a temporary fallback for existing deployments.
    AI_PROVIDER = os.environ.get("AI_PROVIDER", os.environ.get("CHAT_PROVIDER", "flowise")).lower()
    CHAT_PROVIDER = AI_PROVIDER

    # OpenRouter API (demo/experiment)
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "z-ai/glm-4.5-air:free")
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_SYSTEM_PROMPT = os.environ.get("OPENROUTER_SYSTEM_PROMPT", "You are a helpful assistant.")
    OPENROUTER_REASONING_EFFORT = os.environ.get("OPENROUTER_REASONING_EFFORT")

    # Flowise API (primary)
    FLOWISE_API_URL = os.environ.get("FLOWISE_API_URL")
    FLOWISE_API_KEY = os.environ.get("FLOWISE_API_KEY")
    FLOWISE_TIMEOUT = int(os.environ.get("FLOWISE_TIMEOUT", 120))

    # App
    PORT = int(os.environ.get('PORT', 8080))
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

    # Security
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 1 * 1024 * 1024))  # 1 MB
    MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', 2000))
