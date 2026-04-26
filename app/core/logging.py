import logging

from app.core.config import config_settings

def setup_logging():
    logging.basicConfig(
        level=config_settings.LOG_LEVEL,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )