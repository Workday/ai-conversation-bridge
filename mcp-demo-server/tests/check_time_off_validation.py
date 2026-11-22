"""Assert request_my_time_off validates dates, eligibility and balance.

Run: python tests/check_time_off_validation.py   (from mcp-demo-server/, with fastmcp installed)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main  # noqa: E402


def _error(**kwargs: str) -> str:
    result = main.request_my_time_off(**kwargs)
    assert "error" in result and "status" not in result, result
    return result["error"]


def main_check() -> None:
    main.CURRENT_USER_WORKER_ID = "WK001"  # vacation: 12 available; marriage eligible

    ok = main.request_my_time_off("2026-05-20", "2026-05-21", "Vacation", "trip")
    assert ok["status"] == "submitted" and ok["type"] == "vacation", ok

    # Single-day request (start == end) is valid.
    assert main.request_my_time_off("2026-05-20", "2026-05-20", "sick")["status"] == "submitted"

    # Existing check still applies.
    assert "Invalid time-off type" in _error(start_date="2026-05-20", end_date="2026-05-21", time_off_type="sabbatical")

    # Date parsing and ordering.
    assert "Invalid date" in _error(start_date="not-a-date", end_date="2026-05-01", time_off_type="vacation")
    assert "Invalid date" in _error(start_date="2026-05-01", end_date="2026-13-40", time_off_type="vacation")
    assert "Invalid date" in _error(start_date="2026-5-1", end_date="2026-05-02", time_off_type="vacation")
    assert "Invalid date" in _error(start_date="2026-05-01", end_date="2026-05-02T00:00", time_off_type="vacation")
    assert "cannot be before" in _error(start_date="2026-05-10", end_date="2026-05-01", time_off_type="vacation")

    # Balance: personal has 2 available, so 3 inclusive days is too many.
    assert "Insufficient personal" in _error(start_date="2026-06-01", end_date="2026-06-03", time_off_type="personal")
    assert main.request_my_time_off("2026-06-01", "2026-06-02", "personal")["status"] == "submitted"

    # No balance record for marriage leave: falls back to the annual entitlement (3 days).
    assert "Insufficient marriage" in _error(start_date="2026-06-01", end_date="2026-06-04", time_off_type="marriage")
    assert main.request_my_time_off("2026-06-01", "2026-06-03", "marriage")["status"] == "submitted"

    # Eligibility: WK002 is not eligible for marriage leave.
    main.CURRENT_USER_WORKER_ID = "WK002"
    assert "not eligible" in _error(start_date="2026-06-01", end_date="2026-06-02", time_off_type="marriage")

    # A worker with no eligibility record is refused rather than approved.
    main.CURRENT_USER_WORKER_ID = "WK999"
    assert "No eligibility data" in _error(start_date="2026-06-01", end_date="2026-06-02", time_off_type="vacation")

    print("check_time_off_validation: ok")


if __name__ == "__main__":
    main_check()
