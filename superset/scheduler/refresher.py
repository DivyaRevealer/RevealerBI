from __future__ import annotations
import json

import os
import requests
from typing import Any, Dict
from requests import RequestException


def login_superset() -> str:
    print("✅ inside  login_superset")
    """Authenticate with Superset and return a JWT access token."""
    url = os.environ.get("SUPERSET_URL", "http://localhost:8088")
    print(url)
    username = os.environ.get("SUPERSET_USERNAME", "admin")
    password = os.environ.get("SUPERSET_PASSWORD", "admin")
    print(username)
    print(password)
    payload = {
        "username": username,
        "password": password,
        "provider": "db",
    }
    resp = requests.post(f"{url}/api/v1/security/login", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]


def _get_object_id(endpoint: str, filter_column: str, value: str, token: str) -> int:
    """Generic helper to fetch an object's ID from Superset by filtering."""
    url = os.environ.get("SUPERSET_URL", "http://localhost:8088")
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": json.dumps({"filters": [{"col": filter_column, "opr": "eq", "value": value}]})
    }
    resp = requests.get(f"{url}/api/v1/{endpoint}/", params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("count"):
        return data["result"][0]["id"]
    raise ValueError(f"{endpoint.rstrip('/')} '{value}' not found")


def get_dashboard_id(name: str, token: str) -> int:
    """Return the dashboard ID for the given dashboard name."""
    return _get_object_id("dashboard", "dashboard_title", name, token)


def get_database_id(name: str, token: str) -> int:
    """Return the database ID for the given database name."""
    return _get_object_id("database", "database_name", name, token)


def refresh_dashboard(dashboard: int | str, token: str) -> None:
    """Trigger a refresh for the given dashboard."""
    url = os.environ.get("SUPERSET_URL", "http://localhost:8088")
    headers = {"Authorization": f"Bearer {token}"}
    dashboard_id = (
        get_dashboard_id(dashboard, token) if isinstance(dashboard, str) else dashboard
    )
    try:
        resp = requests.post(
            f"{url}/api/v1/dashboard/{dashboard_id}/refresh", headers=headers, timeout=30
        )
        resp.raise_for_status()
    except RequestException as exc:
        print(f"Failed to refresh dashboard {dashboard_id}: {exc}")


def run_sql_query(job: Dict[str, Any], token: str) -> None:
    """Execute a SQL query defined in the job configuration."""
    url = os.environ.get("SUPERSET_URL", "http://localhost:8088")
    payload = {"sql": job["sql"]}
    if "database_id" in job:
        payload["database_id"] = job["database_id"]
    elif "database_name" in job:
        payload["database_id"] = get_database_id(job["database_name"], token)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(
            f"{url}/api/v1/sql/execute", json=payload, headers=headers, timeout=30
        )
        resp.raise_for_status()
    except RequestException as exc:
        print(f"Failed to execute SQL job: {exc}")