"""Scheduler logic."""

import time
from sqlalchemy.orm import Session
from app.core import rabbitmq
from app.db.session import get_db_session
from app.db_utils import job_crud
from app.db_utils.job_crud import fetch_and_mark_running, handle_job_failure, update_job_status
from app.handlers import log_handler


def run_scheduler():
    print("Scheduler started...")

    while True:
        print("Polling Database...")

        try:
            with get_db_session() as db:
                jobs = fetch_and_mark_running(db)

            for job in jobs:
                try:
                    rabbitmq.publish_job(job.id)
                except Exception as e:
                    print(f"Error publishing job {job.id} in the Message queue: {e}")

        except Exception as e:
            print("Scheduler loop error:", e)

        time.sleep(5)