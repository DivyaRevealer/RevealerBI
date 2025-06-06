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
    
    """Load scheduler jobs from ``JOBS_FILE`` and execute them."""
    print("✅ run_jobs")
    #with open(JOBS_FILE) as handle:
     #  jobs = json.load(handle)
    jobs: dict[str, dict] = {}
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE) as handle:
            jobs = json.load(handle)
    #else:
     #   jobs = {}

    print("✅ Before logging into Superset")
    token = login_superset()
    print("✅ Logged into Superset")
    print(token)

    for job in jobs.values():
        print("inside for loop")
        dashboard = job.get("dashboard_id") or job.get("dashboard_name")
        print(dashboard)
        if dashboard:
            refresh_dashboard(dashboard, token)
            print("✅ Dashboard refreshed")

        if "sql" in job:
            run_sql_query(job, token)
            print("✅ SQL query executed")


def start_scheduler() -> BackgroundScheduler:
    """Start the APScheduler background scheduler with a persistent job store."""
    print("✅ inside start_scheduler")
    jobstore_url = os.environ.get(
        "SCHEDULER_JOBSTORE_URL", "sqlite:///scheduler_jobs.sqlite"
    )
    scheduler = BackgroundScheduler(
        jobstores={"default": SQLAlchemyJobStore(url=jobstore_url)}
    )
    print("✅ before add_job")
    #scheduler.add_job(
     #   run_jobs,
     #   "cron",
     #   hour=18,
     #   minute=45,
     #   id="run_jobs",
     #   replace_existing=True,
    #)
    
    scheduler.add_job(
        run_jobs,
        "date",  # runs once immediately
        run_date=None,  # means "now"
        id="run_jobs_now",
        replace_existing=True,
    )
    print("✅ after add_job now")
    scheduler.start()
    print("✅ scheduler started")
    return scheduler

print("✅ File loaded")
if __name__ == "__main__":
    print("✅ inside main")
    sched = start_scheduler()
    print("✅ after sched ")
    print(sched)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sched.shutdown()