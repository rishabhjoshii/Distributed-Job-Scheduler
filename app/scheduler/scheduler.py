"""Scheduler logic."""

import time
from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.db_utils.job_crud import fetch_and_mark_running, update_job_status
from app.handlers import log_handler


def run_scheduler():
    try: 
        print("Scheduler started...")

        while True:
            print("Polling Database...")
            with get_db_session() as db:
                jobs = fetch_and_mark_running(db)

            for job in jobs:
                print(f"Executing job {job.id}")

                with get_db_session() as exec_db:
                    try:
                        log_handler.execute(job)
                        update_job_status(exec_db, job.id, "success")
                    except Exception as e:
                        update_job_status(exec_db, job.id, "failed", str(e))

            time.sleep(5)
            
    except Exception as e:
        print("Scheduler crashed:", e)
