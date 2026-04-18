"""Scheduler logic."""

import time
from sqlalchemy.orm import Session
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
                    if job.retry_count > 0:
                        print(f"Retrying job {job.id}")
                    else:
                        print(f"Executing job {job.id}")

                    with get_db_session() as exec_db:
                        try:
                            log_handler.execute(job)
                            update_job_status(exec_db, job.id, "success")

                        except Exception as e:
                            handle_job_failure(exec_db, job.id, e)

                except Exception as e:
                    print(f"Error processing job {job.id}: {e}")

        except Exception as e:
            print("Scheduler loop error:", e)

        time.sleep(5)