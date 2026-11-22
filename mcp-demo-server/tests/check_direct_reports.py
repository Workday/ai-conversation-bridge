"""Assert get_direct_reports returns a consistent list shape.

Run: python tests/check_direct_reports.py   (from mcp-demo-server/, with fastmcp installed)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main  # noqa: E402


def main_check() -> None:
    # A manager with reports: every item is a real worker record.
    reports = main.get_direct_reports("WK010")
    assert isinstance(reports, list) and reports, reports
    for report in reports:
        assert set(report) == {"worker_id", "name", "title", "department"}, report

    # A worker with no reports: an empty list, not a pseudo-record.
    assert main.get_direct_reports("WK001") == []
    assert main.get_direct_reports("NOT-A-WORKER") == []

    # Empty argument falls back to the current user (WK001 has no reports).
    assert main.get_direct_reports() == main.get_direct_reports(main.CURRENT_USER_WORKER_ID)

    print("check_direct_reports: ok")


if __name__ == "__main__":
    main_check()
