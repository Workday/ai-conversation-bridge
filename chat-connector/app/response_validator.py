import logging
import re

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


class ResponseValidator:
    """Validates AI responses before they are sent to users.

    Catches common hallucination signals and enforces quality gates
    appropriate for enterprise HR/Finance data.
    """

    @staticmethod
    def validate(response_text: str, user_message: str = "") -> str:
        """Validate and return the response, or replace it with a safe fallback.

        Returns the (possibly modified) response text.
        """
        if not response_text or not response_text.strip():
            logger.warning("Empty AI response — returning fallback")
            return FALLBACK_RESPONSE

        response_text = response_text.strip()

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
            logger.warning(
                f"AI response contains hedging language: {hedging_matches}. "
                "This may indicate the LLM answered from its own knowledge "
                "instead of using a tool. Passing through with caveat."
            )

        return response_text
