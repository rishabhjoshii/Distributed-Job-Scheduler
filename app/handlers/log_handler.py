"""Log job handler."""
import logging

from app.handlers.base_handler import JobHandler

logger = logging.getLogger("LogHandler")


class LogHandler(JobHandler):
    def execute(self, job):
        logger.info("Log job payload: %s", job.payload)

