"""Webhook job handler."""
import logging

from app.handlers.base_handler import JobHandler

logger = logging.getLogger("WebhookHandler")


class WebhookHandler(JobHandler):
    def execute(self, job):
        logger.info("Calling webhook with payload: %s", job.payload)