from __future__ import annotations
import json
import logging
import os
from uuid import uuid4

from flask import request, Response
from flask_appbuilder.api import expose, protect, safe

from superset.views.base_api import BaseSupersetApi

logger = logging.getLogger(__name__)

# simple in-memory store for scheduled jobs
JOBS_FILE = os.environ.get("SCHEDULER_JOBS_FILE", "/app/scheduler_jobs.json")

try:
    with open(JOBS_FILE) as handle:
        scheduled_jobs: dict[str, dict] = json.load(handle)
except Exception:
    scheduled_jobs: dict[str, dict] = {}


class SchedulerRestApi(BaseSupersetApi):
    resource_name = "scheduler"
    allow_browser_login = True
    openapi_spec_tag = "Scheduler"

    @expose("/jobs", methods=("GET",))
    @protect()
    @safe
    def list_jobs(self) -> Response:
        """Return a list of scheduled jobs"""
        return self.response(200, result=list(scheduled_jobs.values()))

    @expose("/jobs", methods=("POST",))
    @protect()
    @safe
    def save_job(self) -> Response:
        """Save a scheduler configuration"""
        payload = request.json or {}
        job_id = str(uuid4())
        job = {"id": job_id, **payload}
        scheduled_jobs[job_id] = job
        with open(JOBS_FILE, "w") as handle:
        json.dump(scheduled_jobs, handle)
        logger.info("Saved scheduler job %s", job_id)
        return self.response(201, result=job)

    @expose("/jobs/<job_id>", methods=("DELETE",))
    @protect()
    @safe
    def delete_job(self, job_id: str) -> Response:
        """Delete a scheduled job"""
        if job_id not in scheduled_jobs:
            return self.response_404()
        scheduled_jobs.pop(job_id, None)
        with open(JOBS_FILE, "w") as handle:
        json.dump(scheduled_jobs, handle)
        logger.info("Deleted scheduler job %s", job_id)
        return self.response(200, message="Deleted")