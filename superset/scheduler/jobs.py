from __future__ import annotations

import json
import time
import os

JOBS_FILE = os.environ.get("SCHEDULER_JOBS_FILE", "/app/scheduler_jobs.json")
os.makedirs(os.path.dirname(JOBS_FILE), exist_ok=True)

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
print("✅ Starting jobs.py")

from superset.scheduler.refresher import login_superset, refresh_dashboard, run_sql_query

print("✅ Imported refresher functions")

def run_jobs() -> None:
    """Load jobs from ``scheduler_jobs.json`` and execute them."""
    """Load scheduler jobs from ``JOBS_FILE`` and execute them."""
    with open(JOBS_FILE) as handle:
       jobs = json.load(handle)
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE) as handle:
            jobs = json.load(handle)
    else:
        jobs = {}


    token = login_superset()
    print("✅ Logged into Superset")

    for job in jobs.values():
        dashboard = job.get("dashboard_id") or job.get("dashboard_name")
        if dashboard:
            refresh_dashboard(dashboard, token)
            print("✅ Dashboard refreshed")

        if "sql" in job:
            run_sql_query(job, token)
            print("✅ SQL query executed")


def start_scheduler() -> BackgroundScheduler:
    """Start the APScheduler background scheduler with a persistent job store."""
    jobstore_url = os.environ.get(
        "SCHEDULER_JOBSTORE_URL", "sqlite:///scheduler_jobs.sqlite"
    )
    scheduler = BackgroundScheduler(
        jobstores={"default": SQLAlchemyJobStore(url=jobstore_url)}
    )
    scheduler.add_job(
        run_jobs,
        "cron",
        hour=12,
        minute=11,
        id="run_jobs",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    sched = start_scheduler()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sched.shutdown()