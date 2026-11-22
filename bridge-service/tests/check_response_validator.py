"""Assert ResponseValidator hedging policy: warn by default, fail closed on opt-in.

Run: PYTHONPATH=. python tests/check_response_validator.py
"""

from __future__ import annotations

from app.core.response_validator import FALLBACK_RESPONSE, ResponseValidator


def main() -> None:
    hedged = "I think you probably have 12 days left"

    # Default is unchanged: hedged text is logged but still delivered.
    assert ResponseValidator.validate(hedged) == hedged
    assert ResponseValidator.validate(hedged, block_hedging=False) == hedged

    # Opt-in fails closed for every hedging pattern.
    assert ResponseValidator.validate(hedged, block_hedging=True) == FALLBACK_RESPONSE
    for text in (
        "Maybe 5 days.",
        "My best guess is 8 days.",
        "From what I remember, it is 3 days.",
    ):
        assert ResponseValidator.validate(text, block_hedging=True) == FALLBACK_RESPONSE, text

    # Confident, tool-grounded text is untouched either way.
    grounded = "You have 12 vacation days remaining."
    assert ResponseValidator.validate(grounded, block_hedging=True) == grounded
    assert ResponseValidator.validate(grounded) == grounded

    print("response validator checks passed")


if __name__ == "__main__":
    main()
