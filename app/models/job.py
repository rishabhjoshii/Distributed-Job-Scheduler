"""Job model."""
import uuid
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.db.session import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    type = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)

    status = Column(String, nullable=False, default="pending")

    scheduled_at = Column(TIMESTAMP, nullable=False)

    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    last_error = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
