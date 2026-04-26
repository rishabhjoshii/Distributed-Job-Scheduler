"""Email job handler."""
import logging
import random

from app.handlers.base_handler import JobHandler

logger = logging.getLogger("EmailHandler")


class EmailHandler(JobHandler):
    def execute(self, job):
        logger.info("Sending email with payload: %s", job.payload)
        if random.random() < 0.3:
            raise Exception(f"Simulated failure for job {job.id}")