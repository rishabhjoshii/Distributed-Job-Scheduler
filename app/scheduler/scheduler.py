"""Scheduler logic."""

import logging
import time

from app.core import rabbitmq

logger = logging.getLogger("Scheduler")
from app.db.session import get_db_session
from app.db_utils.job_crud import fetch_pending_jobs, recover_stuck_jobs


def run_scheduler():
    logger.info("Scheduler started...")

    while True:
        logger.info("Polling Database...")

        try:
            with get_db_session() as db:
                recover_stuck_jobs(db)
                jobs = fetch_pending_jobs(db)

            for job in jobs:
                try:
                    logger.info("Publishing job %s to message-queue", job.id)
                    rabbitmq.publish_job(job.id)
                except Exception:
                    logger.exception(
                        "Error publishing job %s in the Message queue", job.id
                    )

        except Exception:
            logger.exception("Scheduler loop error")

        time.sleep(5)