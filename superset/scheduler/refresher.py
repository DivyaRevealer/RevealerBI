from __future__ import annotations
import json

import os
import requests
from typing import Any, Dict
from requests import RequestException, Session


#def login_superset() -> str:
def login_superset() -> Session:
    print("✅ inside  login_superset")
    """Authenticate with Superset and return a JWT access token."""
    """Authenticate with Superset and return an authenticated session."""
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
    #resp = requests.post(f"{url}/api/v1/security/login", json=payload, timeout=10)
    session = requests.Session()
    resp = session.post(f"{url}/api/v1/security/login", json=payload, timeout=10)
    resp.raise_for_status()
    access_token = resp.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {access_token}"})
    csrf = session.get(f"{url}/api/v1/security/csrf_token/", timeout=10)
    csrf.raise_for_status()
    csrf_token = csrf.json()["result"]
    session.headers.update({"X-CSRFToken": csrf_token})
    return session
    
    
    #return resp.json()["access_token"]


#def _get_object_id(endpoint: str, filter_column: str, value: str, token: str) -> int:
def _get_object_id(endpoint: str, filter_column: str, value: str, session: Session) -> int:
    """Generic helper to fetch an object's ID from Superset by filtering."""
    url = os.environ.get("SUPERSET_URL", "http://localhost:8088")
    #headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": json.dumps({"filters": [{"col": filter_column, "opr": "eq", "value": value}]})
    }
    #resp = requests.get(f"{url}/api/v1/{endpoint}/", params=params, headers=headers, timeout=30)
    resp = session.get(f"{url}/api/v1/{endpoint}/", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("count"):
        return data["result"][0]["id"]
    raise ValueError(f"{endpoint.rstrip('/')} '{value}' not found")


#def get_dashboard_id(name: str, token: str) -> int:
def get_dashboard_id(name: str, session: Session) -> int:
    """Return the dashboard ID for the given dashboard name."""
    #return _get_object_id("dashboard", "dashboard_title", name, token)
    return _get_object_id("dashboard", "dashboard_title", name, session)


#def get_database_id(name: str, token: str) -> int:
def get_database_id(name: str, session: Session) -> int:
    """Return the database ID for the given database name."""
    #return _get_object_id("database", "database_name", name, token)
    return _get_object_id("database", "database_name", name, session)


#def refresh_dashboard(dashboard: int | str, token: str) -> None:
def refresh_dashboard(dashboard: int | str, session: Session) -> None:
    """Trigger a refresh for the given dashboard."""
    url = os.environ.get("SUPERSET_URL", "http://localhost:8088")
    #headers = {"Authorization": f"Bearer {token}"}
    dashboard_id = (
        #get_dashboard_id(dashboard, token) if isinstance(dashboard, str) else dashboard
         get_dashboard_id(dashboard, session) if isinstance(dashboard, str) else dashboard
    )
    try:
        #resp = requests.post(
        #resp = requests.put(
        #    f"{url}/api/v1/dashboard/{dashboard_id}/refresh", headers=headers, timeout=30
        #)
        resp = session.put(
            f"{url}/api/v1/dashboard/{dashboard_id}/refresh", timeout=30
        )
        resp.raise_for_status()
    except RequestException as exc:
        print(f"Failed to refresh dashboard {dashboard_id}: {exc}")


#def run_sql_query(job: Dict[str, Any], token: str) -> None:
def run_sql_query(job: Dict[str, Any], session: Session) -> None:
    """Execute a SQL query defined in the job configuration."""
    url = os.environ.get("SUPERSET_URL", "http://localhost:8088")
    #payload = {"sql": job["sql"]}
    
    sql = job.get("sql")
    if not sql:
        print("Skipping SQL job: missing 'sql' field")
        return
    payload = {"sql": sql}

    if "database_id" in job:
        payload["database_id"] = job["database_id"]
    elif "database_name" in job:
        #payload["database_id"] = get_database_id(job["database_name"], token)
         payload["database_id"] = get_database_id(job["database_name"], session)
    #else:
     #   print("Skipping SQL job: missing 'database_id' or 'database_name'")
      #  return
    #headers = {"Authorization": f"Bearer {token}"}
    try:
        #resp = requests.post(
         #    f"{url}/api/v1/sqllab/execute/", json=payload, headers=headers, timeout=30
        resp = session.post(
             f"{url}/api/v1/sqllab/execute/", json=payload, timeout=30
        )
        resp.raise_for_status()
    except RequestException as exc:
        print(f"Failed to execute SQL job: {exc}")