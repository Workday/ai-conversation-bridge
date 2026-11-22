"""Flask routes for chat-platform webhooks and health checks."""

import logging

from flask import Blueprint, current_app, jsonify, request

from app.config import Config
from app.core import async_runner
from app.core.messages import user_message_for
from app.core.prompt_security import wrap_user_input
from app.core.response_validator import ResponseValidator
from app.orchestration.base import OrchestrationRequest
from app.orchestration.errors import FailureCode

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)


@bp.route('/')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "orchestrator": Config.ORCHESTRATOR,
        "ai_provider": Config.AI_PROVIDER,
        "chat_clients": ["lineworks", "dingtalk", "feishu"],
    }), 200


def orchestration_message(user_text: str) -> str:
    """Wrap user text for orchestrators that use prompt-injection guardrails."""
    if Config.ORCHESTRATOR in ("langgraph", "direct_llm"):
        return wrap_user_input(user_text)
    return user_text


def get_ai_response(user_text: str, session_id: str) -> str:
    """Invoke the configured orchestrator and validate the response."""
    orchestrator = current_app.extensions['orchestrator']
    timeout = float(current_app.extensions.get('orchestrator_timeout', Config.FLOWISE_TIMEOUT))
    try:
        result = async_runner.run_coroutine(
            orchestrator.invoke(
                OrchestrationRequest(
                    message=orchestration_message(user_text),
                    session_id=session_id,
                )
            ),
            timeout=timeout + 30.0,
        )
    except TimeoutError:
        logger.error("Orchestration timed out after %.0fs", timeout + 30.0)
        raise
    if result.failure is not None:
        logger.error(
            "Orchestration failure code=%s detail=%s",
            result.failure.value,
            result.detail,
        )
        return user_message_for(result.failure)

    return ResponseValidator.validate(
        str(result.text) if result.text else "",
        user_message=user_text,
    )


def message_too_long_response() -> str:
    """Return the user-facing error message for over-length messages."""
    return f"Your message is too long. Please keep it under {Config.MAX_MESSAGE_LENGTH} characters."


def release_delivery(key: str | None) -> None:
    """Allow a failed delivery to be retried by the chat platform."""
    if not key:
        return
    current_app.extensions['idempotency'].release(key)


def is_duplicate_delivery(key: str | None) -> bool:
    """Record key and return True when this webhook is a retry of an in-flight or recent delivery."""
    if not key:
        return False
    store = current_app.extensions['idempotency']
    if store.claim(key):
        return False
    logger.info("Ignoring duplicate webhook delivery key=%s", key)
    return True


@bp.route('/callback', methods=['POST'])
@bp.route('/lineworks/callback', methods=['POST'])
def lineworks_callback():
    """Handle LINE WORKS message callbacks."""
    try:
        lw_client = current_app.extensions['lw_client']
        lineworks_adapter = current_app.extensions['lineworks_adapter']

        raw_body = request.get_data()
        signature = request.headers.get("X-WORKS-Signature", "")

        if not lineworks_adapter.verify_signature(raw_body, signature):
            current_app.logger.warning("Webhook signature verification failed")
            return 'Unauthorized', 401

        data = request.get_json(silent=True)
        if data is None:
            current_app.logger.warning("Invalid or empty JSON body")
            return 'Bad Request', 400

        current_app.logger.info(
            f"Received callback from user: {data.get('source', {}).get('userId', 'unknown')}"
        )

        message = lineworks_adapter.parse_inbound(data)
        if message is None:
            return 'OK', 200

        if not lw_client.validate_config():
            current_app.logger.error("Missing one or more LINE WORKS environment variables.")
            return 'Internal Server Error', 500

        if lineworks_adapter.is_over_length(message):
            lw_client.send_message(message.reply_target, {
                "content": {
                    "type": "text",
                    "text": message_too_long_response()
                }
            })
            return 'OK', 200

        delivery_key = lineworks_adapter.idempotency_key(raw_body)
        if is_duplicate_delivery(delivery_key):
            return 'OK', 200

        try:
            ai_response_text = get_ai_response(message.text, session_id=message.session_id)

            reply_content = {
                "content": {
                    "type": "text",
                    "text": ai_response_text
                }
            }

            lw_client.send_message(message.reply_target, reply_content)
            current_app.logger.info(f"Sent reply to user {message.sender_id}")
        except TimeoutError:
            release_delivery(delivery_key)
            lw_client.send_message(message.reply_target, {
                "content": {
                    "type": "text",
                    "text": user_message_for(FailureCode.TIMEOUT),
                }
            })
        except Exception:
            release_delivery(delivery_key)
            raise

        return 'OK', 200

    except Exception as e:
        current_app.logger.error(f"Error processing callback: {e}")
        return 'Internal Server Error', 500


@bp.route('/dingtalk/callback', methods=['POST'])
def dingtalk_callback():
    """Handle DingTalk HTTP-mode robot callbacks."""
    try:
        dingtalk_client = current_app.extensions['dingtalk_client']
        dingtalk_adapter = current_app.extensions['dingtalk_adapter']

        data = request.get_json(silent=True)
        if data is None:
            current_app.logger.warning("Invalid or empty DingTalk JSON body")
            return 'Bad Request', 400

        message = dingtalk_adapter.parse_inbound(data)
        if message is None:
            return 'OK', 200

        should_process, reason = dingtalk_adapter.should_process_payload(message, data)
        if not should_process:
            current_app.logger.info(reason)
            return 'OK', 200

        delivery_key = dingtalk_adapter.idempotency_key(data)
        if is_duplicate_delivery(delivery_key):
            return 'OK', 200

        if dingtalk_adapter.is_over_length(message):
            current_app.logger.warning(
                f"DingTalk message from {message.sender_id} exceeds max length "
                f"({len(message.text)} > {Config.MAX_MESSAGE_LENGTH})"
            )
            try:
                dingtalk_client.send_text(message.reply_target, message_too_long_response())
            except Exception:
                release_delivery(delivery_key)
                raise
            return 'OK', 200

        try:
            ai_response_text = get_ai_response(message.text, session_id=message.session_id)
            dingtalk_client.send_text(message.reply_target, ai_response_text)
            current_app.logger.info(f"Sent DingTalk reply to user {message.sender_id}")
        except TimeoutError:
            release_delivery(delivery_key)
            dingtalk_client.send_text(
                message.reply_target, user_message_for(FailureCode.TIMEOUT)
            )
        except Exception:
            release_delivery(delivery_key)
            raise

        return 'OK', 200

    except Exception as e:
        current_app.logger.error(f"Error processing DingTalk callback: {e}")
        return 'Internal Server Error', 500


@bp.route('/feishu/callback', methods=['POST'])
def feishu_callback():
    """Handle Feishu (Lark) event subscription callbacks."""
    feishu_client = current_app.extensions['feishu_client']
    feishu_adapter = current_app.extensions['feishu_adapter']

    body = request.get_json(silent=True) or {}
    logger.info("Feishu callback received")

    if feishu_adapter.is_encrypted(body):
        logger.error(
            "Feishu Encrypt Key is enabled but payload decryption is not implemented; "
            "disable Encrypt Key in the Feishu developer console or add decryption support."
        )
        return jsonify({
            "error": (
                "Encrypted payloads are not supported. "
                "Disable Encrypt Key in your Feishu app event subscription settings."
            )
        }), 400

    if feishu_adapter.is_url_verification(body):
        if feishu_adapter.verify_url_token(body):
            return jsonify({"challenge": body.get("challenge")})
        logger.error("Feishu URL verification token mismatch")
        return jsonify({"error": "Forbidden"}), 403

    if not Config.FEISHU_VERIFICATION_TOKEN:
        logger.error("FEISHU_VERIFICATION_TOKEN is not configured; rejecting Feishu event")
        return jsonify({"error": "Forbidden"}), 403
    if not feishu_adapter.verify_event_token(body):
        logger.error("Feishu event verification token mismatch")
        return jsonify({"error": "Forbidden"}), 403

    event_type = feishu_adapter.event_type(body)

    if event_type == "im.message.receive_v1":
        try:
            event = body.get("event") or {}
            message = feishu_adapter.parse_inbound(event)
            if message is None:
                return jsonify({"code": 0, "msg": "ok"}), 200

            if not feishu_client.validate_config():
                logger.error("Feishu configuration incomplete")
                return jsonify({"code": 0, "msg": "ok"}), 200

            delivery_key = feishu_adapter.idempotency_key(event)
            if is_duplicate_delivery(delivery_key):
                return jsonify({"code": 0, "msg": "ok"}), 200

            if feishu_adapter.is_over_length(message):
                try:
                    feishu_client.send_text_to_chat(
                        message.reply_target, message_too_long_response()
                    )
                except Exception as e:
                    logger.error("Failed to send length limit message: %s", e)
                return jsonify({"code": 0, "msg": "ok"}), 200

            try:
                ai_reply = get_ai_response(message.text, session_id=message.session_id)
                send_result = feishu_client.send_text_to_chat(message.reply_target, ai_reply)
                if isinstance(send_result, dict) and send_result.get("code") != 0:
                    logger.error("Feishu send returned error payload: %s", send_result)
                    release_delivery(delivery_key)
                    return jsonify({"error": "Feishu send failed"}), 502
            except TimeoutError:
                release_delivery(delivery_key)
                feishu_client.send_text_to_chat(
                    message.reply_target, user_message_for(FailureCode.TIMEOUT)
                )
            except Exception as e:
                release_delivery(delivery_key)
                logger.error("Feishu error while processing message: %s", e)
                try:
                    feishu_client.send_text_to_chat(
                        message.reply_target,
                        "Sorry, an error occurred while processing your request. "
                        "Please try again later or contact support.",
                    )
                except Exception as send_err:
                    logger.error("Failed to send error message: %s", send_err)
        except Exception as e:
            logger.exception("Error processing Feishu callback: %s", e)
            return 'Internal Server Error', 500
        return jsonify({"code": 0, "msg": "ok"}), 200

    logger.info("Ignoring Feishu event_type=%s", event_type)
    return jsonify({"code": 0, "msg": "ok"}), 200
