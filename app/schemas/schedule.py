from uuid import UUID
from pydantic import BaseModel, field_validator
from typing import Dict, Any, Optional, Literal
from datetime import datetime

from app.core.constants import VALID_JOB_TYPES, VALID_SCHEDULE_TYPES


class ScheduleCreate(BaseModel):
    type: str
    payload: Dict[str, Any]

    schedule_type: str

    schedule_config: Dict[str, Any]

    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    max_runs: Optional[int] = None

    @field_validator("type")
    @classmethod
    def validate_job_type(cls, val):
        normalized = val.lower()
        if normalized not in VALID_JOB_TYPES:
            allowed = ", ".join(sorted(VALID_JOB_TYPES))
            raise ValueError(f"job type must be one of: {allowed}")
        return normalized

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, val):
        if not val:
            raise ValueError("payload cannot be empty")
        return val

    @field_validator("schedule_type")
    @classmethod
    def validate_schedule_type(cls, val):
        normalized = val.lower()
        if normalized not in VALID_SCHEDULE_TYPES:
            allowed = ", ".join(sorted(VALID_SCHEDULE_TYPES))
            raise ValueError(f"invalid schedule type; must be one of: {allowed}")
        return normalized

    @field_validator("schedule_config")
    @classmethod
    def validate_schedule_config(cls, config, values):
        if values.data.get("schedule_type").lower() == "interval":
            interval = config.get("interval_seconds")

            if interval is None:
                raise ValueError("interval_seconds required")

            if interval <= 0:
                raise ValueError("interval_seconds must be > 0")

        return config

class ScheduleResponse(BaseModel):
    id: UUID
    type: str
    payload: Dict[str, Any]
    schedule_type: str
    schedule_config: Dict[str, Any]
    next_run_at: datetime
    end_at: Optional[datetime]
    max_runs: Optional[int]
    run_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True