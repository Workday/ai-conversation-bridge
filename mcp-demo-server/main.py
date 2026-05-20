"""Mock Workday MCP server for development and testing."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "mock_data"

CURRENT_USER_WORKER_ID = os.environ.get("CURRENT_USER_WORKER_ID", "WK001")

mcp = FastMCP(
    "Workday Demo MCP Server",
    instructions="A demo MCP server with mock Workday tools for development and testing."
)


def _load_mock_data(filename):
    """Load a JSON mock-data file from the server's mock_data directory."""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath) as f:
            return json.load(f)
    return []


def _find_worker(worker_id):
    """Return the worker record for the given ID, or None if not found."""
    workers = _load_mock_data("workers.json")
    for worker in workers:
        if worker["worker_id"] == worker_id:
            return worker
    return None


@mcp.tool()
def get_today_date_and_day_of_week() -> dict:
    """Get the current date and day of the week."""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "day_of_week": now.strftime("%A"),
        "time": now.strftime("%H:%M:%S"),
        "timezone": "server_local"
    }


@mcp.tool()
def find_employee_id_by_name(name: str) -> dict:
    """Search for an employee by name and return their worker ID.

    Args:
        name: Full or partial name to search for
    """
    workers = _load_mock_data("workers.json")
    name_lower = name.lower()
    results = [
        {"worker_id": w["worker_id"], "name": w["name"], "title": w["title"], "department": w["department"]}
        for w in workers
        if name_lower in w.get("name", "").lower()
    ]
    if not results:
        return {"error": f"No employee found matching '{name}'"}
    if len(results) == 1:
        return results[0]
    return {"matches": results, "message": "Multiple employees found. Please clarify which one."}


@mcp.tool()
def get_current_user_info() -> dict:
    """Get profile information for the currently authenticated user.

    Returns name, title, department, manager, location, and hire date.
    """
    worker = _find_worker(CURRENT_USER_WORKER_ID)
    if worker:
        return worker
    return {"error": "Current user not found in system"}


@mcp.tool()
def get_current_user_time_off_balance() -> dict:
    """Get the current user's time-off balances.

    Returns balances for vacation, sick leave, and personal days.
    """
    balances = _load_mock_data("time_off_balances.json")
    for balance in balances:
        if balance["worker_id"] == CURRENT_USER_WORKER_ID:
            return balance
    return {"error": "No time-off balance found for current user"}


@mcp.tool()
def get_current_user_time_off_history() -> dict:
    """Get the current user's time-off request history.

    Returns all past and pending time-off requests.
    """
    history = _load_mock_data("time_off_history.json")
    for record in history:
        if record["worker_id"] == CURRENT_USER_WORKER_ID:
            return record
    return {"worker_id": CURRENT_USER_WORKER_ID, "history": []}


@mcp.tool()
def get_time_off_balance(worker_id: str) -> dict:
    """Get a worker's current time-off balances by worker ID.

    Args:
        worker_id: The worker's ID (e.g. WK001)
    """
    balances = _load_mock_data("time_off_balances.json")
    for balance in balances:
        if balance["worker_id"] == worker_id:
            return balance
    return {"error": f"No time-off balance found for worker {worker_id}"}


@mcp.tool()
def get_direct_reports(worker_id: str = "") -> list[dict]:
    """Get the direct reports for a manager.

    Args:
        worker_id: The manager's worker ID. If empty, uses the current user.
    """
    manager_id = worker_id or CURRENT_USER_WORKER_ID
    workers = _load_mock_data("workers.json")
    reports = [
        {"worker_id": w["worker_id"], "name": w["name"], "title": w["title"], "department": w["department"]}
        for w in workers
        if w.get("manager_id") == manager_id
    ]
    if not reports:
        return [{"message": f"No direct reports found for {manager_id}"}]
    return reports


@mcp.tool()
def get_more_employee_data(worker_id: str) -> dict:
    """Get extended employee data including profile and organizational info.

    Args:
        worker_id: The worker's ID
    """
    worker = _find_worker(worker_id)
    if not worker:
        return {"error": f"Worker {worker_id} not found"}

    personal = _load_mock_data("personal_information.json")
    personal_info = next((p for p in personal if p["worker_id"] == worker_id), {})

    result = {**worker}
    if personal_info:
        result["date_of_birth"] = personal_info.get("date_of_birth")
        result["nationality"] = personal_info.get("nationality")
        result["phone"] = personal_info.get("phone")
    return result


@mcp.tool()
def get_my_time_off_eligibility() -> dict:
    """Get the current user's eligible time-off types and entitlements.

    Returns which leave types the user can request and the annual allocation.
    """
    eligibility = _load_mock_data("time_off_eligibility.json")
    for record in eligibility:
        if record["worker_id"] == CURRENT_USER_WORKER_ID:
            return record
    return {"error": "No eligibility data found for current user"}


@mcp.tool()
def get_personal_information(worker_id: str = "") -> dict:
    """Get personal information for a worker (address, emergency contact, etc.).

    Args:
        worker_id: The worker's ID. If empty, uses the current user.
    """
    target_id = worker_id or CURRENT_USER_WORKER_ID
    personal = _load_mock_data("personal_information.json")
    for record in personal:
        if record["worker_id"] == target_id:
            return record
    return {"error": f"No personal information found for worker {target_id}"}


@mcp.tool()
def request_my_time_off(start_date: str, end_date: str, time_off_type: str, reason: str = "") -> dict:
    """Submit a time-off request for the current user.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        time_off_type: Type of leave (e.g. "vacation", "sick", "personal")
        reason: Optional reason for the request
    """
    valid_types = ["vacation", "sick", "personal", "marriage"]
    if time_off_type.lower() not in valid_types:
        return {"error": f"Invalid time-off type. Must be one of: {valid_types}"}

    return {
        "status": "submitted",
        "request_id": f"TOR-{CURRENT_USER_WORKER_ID}-{start_date}",
        "worker_id": CURRENT_USER_WORKER_ID,
        "start_date": start_date,
        "end_date": end_date,
        "type": time_off_type.lower(),
        "reason": reason,
        "approval_status": "pending_manager_approval"
    }


if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "streamable-http")
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", os.environ.get("MCP_PORT", 8080)))
    path = os.environ.get("MCP_PATH", "/mcp")

    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host=host, port=port, path=path)
    else:
        mcp.run(transport="stdio")
