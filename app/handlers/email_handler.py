"""Email job handler."""
import logging
import random

from app.handlers.base_handler import JobHandler
from app.providers.email.factory import get_email_provider
from app.schemas.job import CreateJobEmailPayload

logger = logging.getLogger("EmailHandler")


class EmailHandler(JobHandler):
    def execute(self, job):
        logger.info("Sending email with payload: %s", job.payload)
        # if random.random() < 0.3:
        #     raise Exception(f"Simulated failure for job {job.id}")

        payload = self.normalize_payload(job.payload, CreateJobEmailPayload)
        
        provider = get_email_provider()

        provider.send_email(
            to=payload.to,
            subject=payload.subject,
            body=payload.body,
            content_type=payload.content_type
        )
        
