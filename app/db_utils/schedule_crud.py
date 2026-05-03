"""CRUD helpers for schedules."""
import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.config import config_settings
from app.core.constants import normalize_value
from app.models.job import Job
from app.models.job_schedule import JobSchedule
from app.schemas.schedule import ScheduleCreate

logger = logging.getLogger("Schedule-Crud-Util")

def fetch_due_schedules(db: Session):
    now = datetime.utcnow()

    stmt = (
        select(JobSchedule)
        .where(
            JobSchedule.is_active == True,
            JobSchedule.next_run_at <= now
        )
        .with_for_update(skip_locked=True)
    )

    result = db.execute(stmt)
    return result.scalars().all()

def create_job_from_schedule(db: Session, schedule):
    logger.info(
        "Creating job from schedule %s (run_count=%s)",
        schedule.id,
        schedule.run_count
    )
    job = Job(
        type=schedule.type,
        payload=schedule.payload,
        scheduled_at=datetime.utcnow(),
        status="pending",
        retry_count=0,
        max_retries=config_settings.DEFAULT_MAX_RETRIES,
        schedule_id=schedule.id
    )

    db.add(job)
    return job

def update_schedule_after_run(db: Session, schedule):
    schedule.run_count += 1

    # stop conditions
    if schedule.max_runs and schedule.run_count >= schedule.max_runs:
        schedule.is_active = False
        return

    if schedule.end_at and schedule.end_at <= datetime.utcnow():
        schedule.is_active = False
        return
    
    if schedule.run_count > config_settings.MAX_SCHEDULE_RUN_COUNT:
        schedule.is_active = False

    # handle interval
    if schedule.schedule_type == "interval":
        interval = schedule.schedule_config.get("interval_seconds", 0)

        if interval <= 0:
            logger.error("Invalid interval for schedule %s", schedule.id)
            schedule.is_active = False
            return

        schedule.next_run_at = schedule.next_run_at + timedelta(seconds=interval)

    else:
        logger.warning(
            "Unsupported schedule_type %s for schedule %s",
            schedule.schedule_type,
            schedule.id
        )

def create_schedule(db: Session, schedule: ScheduleCreate):
    next_run_at = schedule.start_at or datetime.utcnow()

    db_schedule = JobSchedule(
        type=schedule.type,
        payload=schedule.payload,
        schedule_type=schedule.schedule_type,
        schedule_config=schedule.schedule_config,
        next_run_at=next_run_at,
        end_at=schedule.end_at,
        max_runs=schedule.max_runs,
        run_count=0,
        is_active=True
    )

    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)

    return db_schedule

def fetch_schedules(db: Session, status: str, limit: int, offset: int):
    status = normalize_value(status)
    
    if limit > 100: 
        limit = 100

    if offset < 0: 
        offset = 0

    query = db.query(JobSchedule)

    if status == "active":
        query = query.filter(JobSchedule.is_active == True)

    elif status == "inactive":
        query = query.filter(JobSchedule.is_active == False)


    return (
        query
        .order_by(JobSchedule.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def fetch_schedule_by_id(db: Session, schedule_id: str):
    return db.query(JobSchedule).filter(JobSchedule.id == schedule_id).first()


def deactivate_schedule(db: Session, schedule: JobSchedule):
    schedule.is_active = False
    db.commit()
    db.refresh(schedule)
    return schedule

def get_schedule_metrics(db: Session):
    total = db.query(func.count(JobSchedule.id)).scalar() or 0

    active = db.query(func.count(JobSchedule.id)).filter(
        JobSchedule.is_active == True
    ).scalar() or 0

    inactive = db.query(func.count(JobSchedule.id)).filter(
        JobSchedule.is_active == False
    ).scalar() or 0

    avg_runs = db.query(func.avg(JobSchedule.run_count)).scalar() or 0

    return {
        "total_schedules": total,
        "active_schedules": active,
        "inactive_schedules": inactive,
        "avg_runs_per_schedule": round(avg_runs, 2),
    }
