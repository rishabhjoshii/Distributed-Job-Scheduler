"""Log job handler."""
import logging
import random

from app.handlers.base_handler import JobHandler

logger = logging.getLogger("LogHandler")


class LogHandler(JobHandler):
    def execute(self, job):
        logger.info("Log job payload: %s", job.payload)
        # if random.random() < 0.3:
        #     raise Exception(f"Simulated failure for job {job.id}")

