"""Application configuration."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"


class ConfigSettings(BaseSettings):
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_POOL_MAX_OVERFLOW: int = 20

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672

    JOB_QUEUE: str = "job_queue"
    DLQ_QUEUE: str = "job_dlq"

    SCHEDULER_POLL_INTERVAL: int = 5
    STUCK_JOB_TIMEOUT: int = 60

    MAX_FETCH_LIMIT: int = 10
    WORKER_PREFETCH_COUNT: int = 1

    DEFAULT_MAX_RETRIES: int = 3
    RETRY_BACKOFF_BASE: int = 2
    RECOVER_STUCK_LIMIT: int = 50

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        extra="ignore"
    )


config_settings = ConfigSettings()