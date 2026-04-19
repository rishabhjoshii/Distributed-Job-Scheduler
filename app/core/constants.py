"""Application constants."""

from enum import Enum
from typing import Literal


JobStatusFilter = Literal["all", "pending", "running", "success", "failed"]

JobStates = Literal["pending", "running", "success", "failed"]


class JobState(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    RUNNING = "running"
    SUCCESS = "success"
