"""Job request and response schemas."""
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Literal, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.core.constants import VALID_JOB_TYPES


class JobCreate(BaseModel):
    type: str
    payload: Dict[str, Any]
    scheduled_at: Optional[datetime] = None
    max_retries: Optional[int] = 3

    @field_validator("type")
    @classmethod
    def validate_type(cls, val):
        normalized = val.lower()
        if normalized not in VALID_JOB_TYPES:
            allowed = ", ".join(sorted(VALID_JOB_TYPES))
            raise ValueError(f"Job type must be one of: {allowed}")
        return normalized

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

class RetryJobRequest(BaseModel):
    reset_retry_count: Optional[bool] = True
    scheduled_at: Optional[datetime] = None


class PayloadModel(BaseModel):
    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)


class CreateJobEmailPayload(PayloadModel):
    to: EmailStr
    subject: str
    body: str
    content_type: Literal["text", "html"] = "text"


class CreateJobWebhookPayload(PayloadModel):
    url: str
    method: Literal["POST", "GET", "PATCH", "PUT", "DELETE"]
    data: dict = Field(default_factory=dict)

class CreateJobLogPayload(PayloadModel):
    message: str
