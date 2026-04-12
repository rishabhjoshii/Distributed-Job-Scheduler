"""Job request and response schemas."""
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class JobCreate(BaseModel):
    type: str
    payload: Dict[str, Any]
    scheduled_at: Optional[datetime] = None
    max_retries: Optional[int] = 3

    @field_validator("type")
    @classmethod
    def validate_type(cls, val):
        allowed = ["email", "log", "webhook"]
        if val.lower() not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return val.lower()

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, val):
        if not val:
            raise ValueError("payload cannot be empty")
        return val

    # @model_validator(mode="after")
    # def validate_schedule(self):
    #     if self.scheduled_at and self.scheduled_at < datetime.now():
    #         raise ValueError("scheduled_at cannot be in the past")
    #     return self


class JobResponse(BaseModel):
    id: UUID
    type: str
    status: str
    retry_count: int
    max_retries: int
    scheduled_at: datetime
    last_error: Optional[str]
