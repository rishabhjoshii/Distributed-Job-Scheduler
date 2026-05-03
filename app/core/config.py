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
    MAX_SCHEDULE_RUN_COUNT: int = 10000

    LOG_LEVEL: str = "INFO"

    EMAIL_PROVIDER: str = "None"
    RESEND_API_KEY: str
    EMAIL_FROM: str

    AUTH_ENABLED: bool = True
    AUTH_API_KEYS: str
    AUTH_API_KEY_HEADER: str = "x-api-key"
    AUTH_SKIP_PATHS: str = "/docs,/openapi.json,/favicon.ico,/health-check,/health,/metrics"
    AUTH_PROTECTED_METHODS: str

    @property
    def parsed_api_keys(self):
        return [k.strip() for k in self.AUTH_API_KEYS.split(",") if k.strip()]

    @property
    def parsed_skip_paths(self):
        return [p.strip() for p in self.AUTH_SKIP_PATHS.split(",") if p.strip()]

    @property
    def parsed_protected_methods(self):
        return [m.strip().upper() for m in self.AUTH_PROTECTED_METHODS.split(",") if m.strip()]

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        extra="ignore"
    )


config_settings = ConfigSettings()