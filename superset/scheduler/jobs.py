from __future__ import annotations

import json
import time
import os

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from refresher import login_superset, refresh_dashboard, run_sql_query


def run_jobs() -> None:
    """Load jobs from ``scheduler_jobs.json`` and execute them."""
    with open("/app/scheduler_jobs.json") as handle:
        jobs = json.load(handle)

    token = login_superset()
    for job in jobs:
        refresh_dashboard(job["dashboard_id"], token)
        if "sql" in job:
            run_sql_query(job, token)


def start_scheduler() -> BackgroundScheduler:
        """Start the APScheduler background scheduler with a persistent job store."""
    jobstore_url = os.environ.get(
        "SCHEDULER_JOBSTORE_URL", "sqlite:///scheduler_jobs.sqlite"
    )
    scheduler = BackgroundScheduler(
        jobstores={"default": SQLAlchemyJobStore(url=jobstore_url)}
    )
    scheduler.add_job(run_jobs, "cron", hour=7, minute=0)
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    sched = start_scheduler()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sched.shutdown()