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


def normalize_value(value: str) -> str:
    return (value or "").strip().lower()


def normalize_status_filter(status: str) -> str:
    normalized = normalize_value(status)
    if normalized not in VALID_JOB_STATUS_FILTERS:
        raise ValueError(f"Invalid job status filter: {status}")
    return normalized
