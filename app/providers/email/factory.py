from app.core.config import config_settings
from app.providers.email.resend_provider import ResendProvider
from app.providers.email.dummy_provider import DummyEmailProvider
import logging

logger = logging.getLogger("EmailProviderFactory")


def get_email_provider():
    provider = config_settings.EMAIL_PROVIDER.lower()

    if provider == "resend":
        logger.info("Using Resend email provider")
        return ResendProvider()

    # fallback provider
    logger.error(
        "Invalid EMAIL_PROVIDER '%s'. Falling back to DummyEmailProvider",
        provider
    )
    return DummyEmailProvider()
