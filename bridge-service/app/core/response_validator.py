"""Validation helpers for AI responses before delivery to chat users."""

import logging
import re

from app.core.prompt_security import response_contains_canary_leak

logger = logging.getLogger(__name__)

HEDGING_PATTERNS = [
    r"\bi think\b",
    r"\bprobably\b",
    r"\bmaybe\b",
    r"\bi believe\b",
    r"\bi assume\b",
    r"\bnot sure\b",
    r"\bif i recall\b",
    r"\bfrom what i remember\b",
    r"\bapproximately\b",
    r"\bmy best guess\b",
]

COMPILED_HEDGING = [re.compile(p, re.IGNORECASE) for p in HEDGING_PATTERNS]

MAX_RESPONSE_LENGTH = 4000

FALLBACK_RESPONSE = (
    "I wasn't able to generate a reliable answer. "
    "Please try rephrasing your question, or contact your HR team for assistance."
)

SECURITY_BLOCKED_RESPONSE = "I cannot fulfill this request."


class ResponseValidator:
    """Validates AI responses before they are sent to users.

    Catches common hallucination signals and enforces quality gates
    appropriate for enterprise HR/Finance data.
    """

    @staticmethod
    def validate(
        response_text: str,
        user_message: str = "",
        block_hedging: bool = False,
    ) -> str:
        """Validate and return the response, or replace it with a safe fallback.

        When ``block_hedging`` is True, a response containing hedging language
        is replaced with ``FALLBACK_RESPONSE`` (fail closed) instead of being
        delivered with only a warning. It defaults to False so existing
        deployments keep the warn-and-pass-through behavior.

        Returns the (possibly modified) response text.
        """
        if not response_text or not response_text.strip():
            logger.warning("Empty AI response — returning fallback")
            return FALLBACK_RESPONSE

        response_text = response_text.strip()

        if response_contains_canary_leak(response_text):
            logger.critical("Canary token leak detected in model output; blocking response")
            return SECURITY_BLOCKED_RESPONSE

        if len(response_text) > MAX_RESPONSE_LENGTH:
            logger.warning(
                f"AI response exceeds max length ({len(response_text)} chars) — truncating"
            )
            truncated = response_text[:MAX_RESPONSE_LENGTH]
            last_sentence = max(
                truncated.rfind(". "),
                truncated.rfind(".\n"),
                truncated.rfind("。"),
            )
            if last_sentence > MAX_RESPONSE_LENGTH // 2:
                truncated = truncated[:last_sentence + 1]
            response_text = truncated

        hedging_matches = []
        for pattern in COMPILED_HEDGING:
            if pattern.search(response_text):
                hedging_matches.append(pattern.pattern)

        if hedging_matches:
            if block_hedging:
                logger.warning(
                    f"AI response contains hedging language: {hedging_matches}. "
                    "This may indicate the LLM answered from its own knowledge "
                    "instead of using a tool. Blocking response (fail closed)."
                )
                return FALLBACK_RESPONSE
            logger.warning(
                f"AI response contains hedging language: {hedging_matches}. "
                "This may indicate the LLM answered from its own knowledge "
                "instead of using a tool. Passing through."
            )

        return response_text
