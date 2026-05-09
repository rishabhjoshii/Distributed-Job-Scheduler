"""Webhook job handler."""
import logging
import requests
import random

from app.handlers.base_handler import JobHandler
from app.schemas.job import CreateJobWebhookPayload

logger = logging.getLogger("WebhookHandler")


class WebhookHandler(JobHandler):
    def execute(self, job):
        payload = self.normalize_payload(job.payload, CreateJobWebhookPayload)

        logger.info(
            "Calling webhook → url=%s method=%s",
            payload.url,
            payload.method
        )

        try:
            request_method = payload.method.upper()

            response = requests.request(
                method=request_method,
                url=payload.url,
                json=payload.data if request_method != "GET" else None,
                params=payload.data if request_method == "GET" else None,
                timeout=5
            )

            if response.status_code >= 400:
                raise Exception(
                    f"Webhook failed with status {response.status_code}: {response.text}"
                )

        except Exception as e:
            raise Exception(f"Webhook execution failed: {e}") from e
