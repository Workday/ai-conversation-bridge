import logging

from flask import Blueprint, current_app, jsonify, request

from app.config import Config
from app.services.flowise import FlowiseClient
from app.services.lineworks import LineWorksClient
from app.services.openrouter import OpenRouterClient
from app.response_validator import ResponseValidator

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

lw_client = LineWorksClient(Config)

if Config.CHAT_PROVIDER == 'openrouter':
    logger.info("Using OpenRouter as chat provider (demo/experiment)")
    ai_client = OpenRouterClient(
        Config.OPENROUTER_API_KEY,
        Config.OPENROUTER_MODEL,
        Config.OPENROUTER_API_URL,
        Config.OPENROUTER_SYSTEM_PROMPT,
        Config.OPENROUTER_REASONING_EFFORT
    )
else:
    logger.info("Using Flowise as chat provider")
    ai_client = FlowiseClient(
        Config.FLOWISE_API_URL,
        Config.FLOWISE_API_KEY,
        Config.FLOWISE_TIMEOUT
    )


@bp.route('/')
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "provider": Config.CHAT_PROVIDER}), 200


@bp.route('/callback', methods=['POST'])
def callback():
    """Handle LINE WORKS message callbacks."""
    try:
        raw_body = request.get_data()
        signature = request.headers.get("X-WORKS-Signature", "")

        if not lw_client.verify_signature(raw_body, signature):
            current_app.logger.warning("Webhook signature verification failed")
            return 'Unauthorized', 401

        data = request.get_json(silent=True)
        if data is None:
            current_app.logger.warning("Invalid or empty JSON body")
            return 'Bad Request', 400

        current_app.logger.info(f"Received callback from user: {data.get('source', {}).get('userId', 'unknown')}")

        if not data or data.get('type') != 'message':
            return 'OK', 200

        source = data.get('source')
        user_id = source.get('userId') if source else None

        content_payload = data.get('content', {})
        message_type = content_payload.get('type')
        user_text = content_payload.get('text')

        if not user_id:
            current_app.logger.warning("No userId found in source")
            return 'OK', 200

        if message_type != 'text' or not user_text:
            current_app.logger.info("Received non-text message or empty text.")
            return 'OK', 200

        user_text = user_text.strip()
        if len(user_text) > Config.MAX_MESSAGE_LENGTH:
            current_app.logger.warning(
                f"Message from {user_id} exceeds max length ({len(user_text)} > {Config.MAX_MESSAGE_LENGTH})"
            )
            lw_client.send_message(user_id, {
                "content": {
                    "type": "text",
                    "text": f"Your message is too long. Please keep it under {Config.MAX_MESSAGE_LENGTH} characters."
                }
            })
            return 'OK', 200

        if not lw_client.validate_config():
            current_app.logger.error("Missing one or more LINE WORKS environment variables.")
            return 'Internal Server Error', 500

        ai_response_text = ai_client.get_completion(user_text, user_id=user_id)
        ai_response_text = ResponseValidator.validate(
            str(ai_response_text) if ai_response_text else "",
            user_message=user_text
        )

        reply_content = {
            "content": {
                "type": "text",
                "text": ai_response_text
            }
        }

        lw_client.send_message(user_id, reply_content)
        current_app.logger.info(f"Sent reply to user {user_id}")

        return 'OK', 200

    except Exception as e:
        current_app.logger.error(f"Error processing callback: {e}")
        return 'Internal Server Error', 500
