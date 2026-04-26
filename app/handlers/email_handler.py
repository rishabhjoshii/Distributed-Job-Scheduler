"""Email job handler."""
import logging

from app.handlers.base_handler import JobHandler

logger = logging.getLogger("EmailHandler")


class EmailHandler(JobHandler):
    def execute(self, job):
        logger.info("Sending email with payload: %s", job.payload)