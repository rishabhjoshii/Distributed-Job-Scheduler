from datetime import datetime

from sqlalchemy.orm import Session
from app.db_utils import schedule_crud
from app.models.job_schedule import JobSchedule
from app.schemas.schedule import ScheduleCreate


def create_schedule(db: Session, schedule: ScheduleCreate):
    if schedule.end_at and schedule.start_at and schedule.start_at > schedule.end_at:
        raise ValueError("start_at must be before end_at")

    return schedule_crud.create_schedule(db, schedule)

def list_schedules(db: Session, status: str, limit: int, offset: int):
    return schedule_crud.fetch_schedules(db, status, limit, offset)


def get_schedule(db: Session, schedule_id: str):
    return schedule_crud.fetch_schedule_by_id(db, schedule_id)


def cancel_schedule(db: Session, schedule_id: str):
    schedule = schedule_crud.fetch_schedule_by_id(db, schedule_id)

    if not schedule:
        return None

    return schedule_crud.deactivate_schedule(db, schedule)