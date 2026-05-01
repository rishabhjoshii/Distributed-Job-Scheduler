import logging
from app.providers.email.base import EmailProvider

logger = logging.getLogger("DummyEmail")


class DummyEmailProvider(EmailProvider):
    def send_email(self, to, subject, body, content_type):
        logger.info(
            "Dummy email -> to=%s subject=%s type=%s body=%s",
            to,
            subject,
            content_type,
            body
        )