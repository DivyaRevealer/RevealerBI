from __future__ import annotations

import os
import requests
from typing import Any, Dict


def login_superset() -> str:
    """Authenticate with Superset and return a JWT access token."""
    url = os.environ.get("SUPERSET_URL", "http://localhost:8088")
    username = os.environ.get("SUPERSET_USERNAME", "admin")
    password = os.environ.get("SUPERSET_PASSWORD", "admin")

    payload = {
        "username": username,
        "password": password,
        "provider": "db",
    }
    resp = requests.post(f"{url}/api/v1/security/login", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]


def refresh_dashboard(dashboard_id: int, token: str) -> None:
    """Trigger a refresh for the given dashboard."""
    url = os.environ.get("SUPERSET_URL", "http://localhost:8088")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(
        f"{url}/api/v1/dashboard/{dashboard_id}/refresh", headers=headers, timeout=30
    )
    resp.raise_for_status()


def run_sql_query(job: Dict[str, Any], token: str) -> None:
    """Execute a SQL query defined in the job configuration."""
    url = os.environ.get("SUPERSET_URL", "http://localhost:8088")
    payload = {"sql": job["sql"]}
    if "database_id" in job:
        payload["database_id"] = job["database_id"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{url}/api/v1/sql/execute", json=payload, headers=headers, timeout=30)
    resp.raise_for_status()