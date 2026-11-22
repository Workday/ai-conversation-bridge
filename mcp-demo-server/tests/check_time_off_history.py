"""Assert a submitted time-off request shows up in the user's history.

Run: python tests/check_time_off_history.py   (from mcp-demo-server/, with fastmcp installed)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main  # noqa: E402


def main_check() -> None:
    main.CURRENT_USER_WORKER_ID = "WK001"
    before = main.get_current_user_time_off_history()
    assert before["worker_id"] == "WK001"
    baseline = len(before["history"])
    assert all(e["request_id"] != "TOR-WK001-2026-05-20" for e in before["history"])

    result = main.request_my_time_off("2026-05-20", "2026-05-21", "vacation", "trip")
    assert result["status"] == "submitted", result

    after = main.get_current_user_time_off_history()
    assert len(after["history"]) == baseline + 1, after
    entry = after["history"][-1]
    assert entry["request_id"] == result["request_id"], entry
    assert (entry["type"], entry["start_date"], entry["end_date"], entry["days"]) == (
        "vacation", "2026-05-20", "2026-05-21", 2
    ), entry
    assert entry["status"] == "pending" and "worker_id" not in entry, entry

    # Existing mock history is untouched, and nothing is written back to mock_data/.
    assert after["history"][:baseline] == before["history"]
    assert len(main.get_current_user_time_off_history()["history"]) == baseline + 1
    assert main._load_mock_data("time_off_history.json")[0]["history"] == before["history"]

    # A rejected request is not recorded.
    assert "error" in main.request_my_time_off("2026-05-22", "2026-05-23", "sabbatical")
    assert len(main.get_current_user_time_off_history()["history"]) == baseline + 1

    # Requests are per worker, including a worker with no mock history record.
    main.CURRENT_USER_WORKER_ID = "WK999"
    assert main.get_current_user_time_off_history() == {"worker_id": "WK999", "history": []}
    main.request_my_time_off("2026-07-01", "2026-07-01", "sick")
    other = main.get_current_user_time_off_history()
    assert [e["request_id"] for e in other["history"]] == ["TOR-WK999-2026-07-01"], other
    main.CURRENT_USER_WORKER_ID = "WK001"
    assert len(main.get_current_user_time_off_history()["history"]) == baseline + 1

    print("check_time_off_history: ok")


if __name__ == "__main__":
    main_check()
