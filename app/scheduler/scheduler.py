"""Scheduler logic."""

import logging
import threading
import time

from app.core import rabbitmq
from app.core.config import config_settings
from app.db.session import get_db_session
from app.db_utils.job_crud import fetch_pending_jobs, recover_stuck_queued_jobs, recover_stuck_running_jobs
from app.db_utils.schedule_crud import create_job_from_schedule, fetch_due_schedules, update_schedule_after_run

logger = logging.getLogger("Scheduler")

shutdown_event = threading.Event()

def request_shutdown():
    logger.info("Scheduler shutdown requested")
    shutdown_event.set()

def run_scheduler():
    logger.info("Scheduler started...")

    while not shutdown_event.is_set():
        logger.info("Polling Database...")

        try:
            with get_db_session() as db:
                recover_stuck_running_jobs(db, config_settings.STUCK_JOB_TIMEOUT)
                recover_stuck_queued_jobs(db, config_settings.STUCK_JOB_TIMEOUT)
            
                schedules = fetch_due_schedules(db)
                for schedule in schedules:
                    create_job_from_schedule(db, schedule)
                    update_schedule_after_run(db, schedule)
                    logger.info(
                        "successfully created job from schedule %s (run_count=%s)",
                        schedule.id,
                        schedule.run_count
                    )

                db.commit()

                job_ids = fetch_pending_jobs(db, config_settings.MAX_FETCH_LIMIT)

            for job_id in job_ids:
                try:
                    logger.info("Publishing job %s to message-queue", job_id)
                    rabbitmq.publish_job(job_id)
                except Exception:
                    logger.exception(
                        "Error publishing job %s in the Message queue", job_id
                    )

        except Exception:
            logger.exception("Scheduler loop error")

        time.sleep(config_settings.SCHEDULER_POLL_INTERVAL)
    
    logger.info("Scheduler shutdown complete")