"""Assert ResponseValidator hedging policy: warn by default, fail closed on opt-in.

Run: PYTHONPATH=. python tests/check_response_validator.py
"""

from __future__ import annotations

from app.core.response_validator import (
    FALLBACK_RESPONSE,
    HEDGING_PATTERNS,
    MAX_RESPONSE_LENGTH,
    ResponseValidator,
)


def main() -> None:
    hedged = "I think you probably have 12 days left"

    # Default is unchanged: hedged text is logged but still delivered.
    assert ResponseValidator.validate(hedged) == hedged
    assert ResponseValidator.validate(hedged, block_hedging=False) == hedged

    # Opt-in fails closed for every hedging pattern.
    assert ResponseValidator.validate(hedged, block_hedging=True) == FALLBACK_RESPONSE
    examples = {
        r"\bi think\b": "I think it is 5 days.",
        r"\bprobably\b": "It is probably 5 days.",
        r"\bmaybe\b": "Maybe 5 days.",
        r"\bi believe\b": "I believe it is 5 days.",
        r"\bi assume\b": "I assume it is 5 days.",
        r"\bnot sure\b": "Not sure, 5 days.",
        r"\bif i recall\b": "If I recall, it is 5 days.",
        r"\bfrom what i remember\b": "From what I remember, it is 3 days.",
        r"\bapproximately\b": "Approximately 5 days.",
        r"\bmy best guess\b": "My best guess is 8 days.",
    }
    assert set(examples) == set(HEDGING_PATTERNS), "add an example for every pattern"
    for text in examples.values():
        assert ResponseValidator.validate(text, block_hedging=True) == FALLBACK_RESPONSE, text
        assert ResponseValidator.validate(text) == text, text

    # A hedge beyond the truncation point still fails closed.
    long_hedged = ("Your balance is 12 days. " * 400) + "I think these figures are correct."
    assert len(long_hedged) > MAX_RESPONSE_LENGTH
    assert ResponseValidator.validate(long_hedged, block_hedging=True) == FALLBACK_RESPONSE
    assert len(ResponseValidator.validate(long_hedged)) <= MAX_RESPONSE_LENGTH

    # Confident, tool-grounded text is untouched either way.
    grounded = "You have 12 vacation days remaining."
    assert ResponseValidator.validate(grounded, block_hedging=True) == grounded
    assert ResponseValidator.validate(grounded) == grounded

    print("response validator checks passed")


if __name__ == "__main__":
    main()
