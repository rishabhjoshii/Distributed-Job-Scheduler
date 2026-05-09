"""Shared payload normalization utilities."""

from pydantic import BaseModel

from app.core.constants import normalize_value
from app.schemas.job import (
    CreateJobEmailPayload,
    CreateJobLogPayload,
    CreateJobWebhookPayload,
)


PAYLOAD_SCHEMAS = {
    "email": CreateJobEmailPayload,
    "webhook": CreateJobWebhookPayload,
    "log": CreateJobLogPayload,
}


def get_payload_schema(job_type: str):
    normalized_type = normalize_value(job_type)
    schema_cls = PAYLOAD_SCHEMAS.get(normalized_type)

    if schema_cls is None:
        raise ValueError(f"Unsupported job type: {job_type}")

    return schema_cls


def normalize_payload_model(job_type: str, payload):
    schema_cls = get_payload_schema(job_type)

    if isinstance(payload, schema_cls):
        return payload

    if isinstance(payload, BaseModel):
        payload = payload.model_dump()

    return schema_cls(**payload)


def normalize_payload_dict(job_type: str, payload):
    return normalize_payload_model(job_type, payload).model_dump()


def normalize_payload_with_schema(schema_cls, payload):
    if isinstance(payload, schema_cls):
        return payload

    if isinstance(payload, BaseModel):
        payload = payload.model_dump()

    return schema_cls(**payload)
