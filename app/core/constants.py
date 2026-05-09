"""Application constants."""

from enum import Enum
from typing import Literal


JobStatusFilter = Literal["all", "pending", "running", "queued", "success", "failed"]

JobStates = Literal["pending", "running", "success", "failed", "queued"]

class JobState(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    RUNNING = "running"
    SUCCESS = "success"
    QUEUED = "queued"
    CANCELLED = "cancelled"

class JobType(str, Enum):
    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"


VALID_JOB_STATUS_FILTERS = {
    "all",
    JobState.PENDING.value,
    JobState.RUNNING.value,
    JobState.SUCCESS.value,
    JobState.FAILED.value,
    JobState.QUEUED.value,
}

VALID_CANCELLABLE_JOB_STATES = {
    JobState.PENDING.value,
    JobState.QUEUED.value,
}

ValidScheduleTypes = Literal["interval"]
ValidJobTypes = Literal["webhook", "email", "log"]

# Runtime allow-lists (typing.Literal is not safe for `x in Literal[...]` checks).
VALID_SCHEDULE_TYPES = frozenset({"interval"})
VALID_JOB_TYPES = frozenset({"webhook", "email", "log"})

class ScheduleStatus(str, Enum):
    ALL = "all"
    ACTIVE = "active"
    INACTIVE = "inactive"


def normalize_value(value: str) -> str:
    return (value or "").strip().lower()


def normalize_status_filter(status: str) -> str:
    normalized = normalize_value(status)
    if normalized not in VALID_JOB_STATUS_FILTERS:
        raise ValueError(f"Invalid job status filter: {status}")
    return normalized

def validate_schedule_config(schedule_type, config):
    if schedule_type == "interval":
        interval = config.get("interval_seconds")

        if interval is None:
            raise ValueError("interval_seconds is required for interval schedule")

        if interval <= 0:
            raise ValueError("interval_seconds must be > 0")
