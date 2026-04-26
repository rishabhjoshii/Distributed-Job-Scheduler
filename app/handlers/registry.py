from app.core.constants import JobType
from app.handlers.email_handler import EmailHandler
from app.handlers.log_handler import LogHandler
from app.handlers.webhook_handler import WebhookHandler


HANDLERS = {
    JobType.LOG: LogHandler(),
    JobType.EMAIL: EmailHandler(),
    JobType.WEBHOOK: WebhookHandler(),
}

def get_job_handler(job_type: str):
    return HANDLERS.get(job_type)