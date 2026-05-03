import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base

class JobSchedule(Base):
    __tablename__ = "job_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    type = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)

    schedule_type = Column(String, nullable=False)
    schedule_config = Column(JSONB, nullable=False)

    next_run_at = Column(DateTime, nullable=False)

    end_at = Column(DateTime, nullable=True)
    max_runs = Column(Integer, nullable=True)
    run_count = Column(Integer, default=0, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="schedule")