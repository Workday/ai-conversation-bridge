"""Assert pay slip MCP tools work correctly with mock data.

Run: PYTHONPATH=. python tests/check_payslips.py
"""

from __future__ import annotations

import os
import sys
import types
from pathlib import Path

# Ensure CURRENT_USER_WORKER_ID defaults to WK001 for test fixture
os.environ.setdefault("CURRENT_USER_WORKER_ID", "WK001")

REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_SERVER_DIR = REPO_ROOT / "mcp-demo-server"

# Stub FastMCP if not installed in the environment
if "fastmcp" not in sys.modules:
    try:
        import fastmcp  # noqa: F401
    except ModuleNotFoundError:
        fastmcp_stub = types.ModuleType("fastmcp")

        class MockFastMCP:
            def __init__(self, *args, **kwargs):
                pass

            def tool(self, *args, **kwargs):
                def decorator(fn):
                    return fn

                return decorator

        setattr(fastmcp_stub, "FastMCP", MockFastMCP)
        sys.modules["fastmcp"] = fastmcp_stub

if str(MCP_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_SERVER_DIR))

from main import CURRENT_USER_WORKER_ID, get_current_user_payslips, get_payslip_by_worker_id  # noqa: E402


def main() -> None:
    print("Testing pay slip MCP tools...")

    # 1. Current user all payslips
    all_slips = get_current_user_payslips()
    assert "payslips" in all_slips, f"Expected payslips list, got {all_slips}"
    assert all_slips["worker_id"] == CURRENT_USER_WORKER_ID
    assert len(all_slips["payslips"]) >= 1, f"Expected at least 1 slip for {CURRENT_USER_WORKER_ID}"

    # 2. Worker lookup: WK001 specific periods
    feb_slip = get_payslip_by_worker_id("WK001", "2026-02")
    assert feb_slip.get("period") == "2026-02", f"Expected 2026-02, got {feb_slip}"
    assert feb_slip.get("worker_id") == "WK001"
    assert feb_slip.get("net_pay") == 25200
    assert "deductions" in feb_slip
    assert feb_slip["deductions"]["income_tax"] == 4200

    jan_slip = get_payslip_by_worker_id("WK001", "2026-01")
    assert jan_slip.get("period") == "2026-01"
    assert jan_slip.get("pay_date") == "2026-01-31"

    # 3. Period not found
    missing_period = get_payslip_by_worker_id("WK001", "2025-12")
    assert "error" in missing_period, f"Expected error for 2025-12, got {missing_period}"

    # 4. Worker lookup: WK003 (Tokyo - JPY)
    wk003_slip = get_payslip_by_worker_id("WK003", "2026-02")
    assert wk003_slip.get("worker_id") == "WK003"
    assert wk003_slip.get("currency") == "JPY"
    assert wk003_slip.get("gross_pay") == 650000
    assert wk003_slip.get("net_pay") == 480025

    # 5. Worker lookup: WK004 (Seoul - KRW)
    wk004_all = get_payslip_by_worker_id("WK004")
    assert wk004_all.get("worker_id") == "WK004"
    assert len(wk004_all.get("payslips", [])) == 1
    assert wk004_all["payslips"][0]["currency"] == "KRW"

    # 6. Non-existent worker
    nonexistent = get_payslip_by_worker_id("WK999")
    assert "error" in nonexistent, f"Expected error for WK999, got {nonexistent}"

    print("All pay slip MCP tool checks passed successfully!")


if __name__ == "__main__":
    main()
