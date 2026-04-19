"""Scheduler logic."""

import time
from app.core import rabbitmq
from app.db.session import get_db_session
from app.db_utils.job_crud import fetch_pending_jobs, recover_stuck_jobs


def run_scheduler():
    print("Scheduler started...")

    while True:
        print("Polling Database...")

        try:
            with get_db_session() as db:
                recover_stuck_jobs(db)
                jobs = fetch_pending_jobs(db)

            for job in jobs:
                try:
                    print("Publishing job to message-queue")
                    rabbitmq.publish_job(job.id)
                except Exception as e:
                    print(f"Error publishing job {job.id} in the Message queue: {e}")

        except Exception as e:
            print("Scheduler loop error:", e)

        time.sleep(5)