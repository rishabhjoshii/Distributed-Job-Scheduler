"""Base job handler."""

from abc import ABC, abstractmethod

from app.core.payloads import normalize_payload_with_schema

class JobHandler(ABC):
    def normalize_payload(self, payload, schema_cls):
        return normalize_payload_with_schema(schema_cls, payload)

    @abstractmethod
    def execute(self, job):
        pass
