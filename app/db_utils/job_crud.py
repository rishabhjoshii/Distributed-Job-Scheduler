"""CRUD helpers for jobs."""
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.config import config_settings
from app.core.constants import JobState, normalize_value
from app.core.metrics import metrics
from app.models.job import Job

logger = logging.getLogger("Jobs-Crud-Util")


def create_job(db: Session, job_data):
    job = Job(
        type=job_data.type,
        payload=job_data.payload,
        scheduled_at=job_data.scheduled_at or datetime.utcnow(),
        max_retries=job_data.max_retries or config_settings.DEFAULT_MAX_RETRIES
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise ValueError(f"Job with id {job_id} not found")
    return job


def list_jobs(db: Session, status: str):
    status = normalize_value(status)
    query = db.query(Job)
    if status != "all":
        query = query.filter(Job.status == status)
    return query.order_by(Job.created_at.desc()).all()


def update_job(db: Session, job_id, job_data):
    job = get_job(db, job_id)
    if not job:
        raise ValueError(f"Job with id {job_id} not found")
    job.type = job_data.type
    job.payload = job_data.payload
    job.scheduled_at = job_data.scheduled_at or datetime.utcnow()
    job.max_retries = job_data.max_retries or config_settings.DEFAULT_MAX_RETRIES

    db.commit()
    db.refresh(job)
    return job

def delete_job(db: Session, job_id):
    job = get_job(db, job_id)
    if not job:
        raise ValueError(f"Job with id {job_id} not found")
    db.delete(job)
    db.commit()
    return job


def fetch_pending_jobs(db: Session, limit=10):
    query = (
        select(Job)
        .where(
            Job.status == JobState.PENDING,
            Job.scheduled_at <= datetime.utcnow()
        )
        .order_by(Job.scheduled_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )

    result = db.execute(query)
    jobs = result.scalars().all()

    job_ids = []

    for job in jobs:
        job.status = JobState.QUEUED
        job.queued_at = datetime.utcnow()
        job_ids.append(job.id)

    db.commit()

    return job_ids

def update_job_status(db: Session, job_id, status: JobState, error=None):
    job = get_job(db, job_id)

    if not job:
        return None

    job.status = status
    if error:
        job.last_error = error

    db.commit()
    db.refresh(job)
    return job

def handle_job_failure(db, job_id, error):
    job = get_job(db, job_id)

    if not job:
        return None

    job.last_error = str(error)

    if job.retry_count < job.max_retries:
        delay_seconds = config_settings.RETRY_BACKOFF_BASE ** job.retry_count

        job.status = JobState.PENDING
        job.scheduled_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        job.retry_count += 1

        logger.info(
            "Job %s re-scheduled for %s", job_id, job.scheduled_at
        )
        metrics.jobs_retried += 1

    else:
        job.status = JobState.FAILED

    db.commit()
    return job

def fetch_job_for_update(db, job_id):
    stmt = (
        select(Job)
        .where(Job.id == job_id)
        .with_for_update()
    )

    result = db.execute(stmt)
    return result.scalar_one_or_none()

def recover_stuck_running_jobs(db, timeout_seconds=60, limit=None):
    if limit is None:
        limit = config_settings.RECOVER_STUCK_LIMIT

    threshold = datetime.utcnow() - timedelta(seconds=timeout_seconds)

    stmt = (
        select(Job)
        .where(
            Job.status == JobState.RUNNING,
            Job.updated_at < threshold
        )
        .order_by(Job.updated_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )

    result = db.execute(stmt)
    stuck_jobs = result.scalars().all()

    for job in stuck_jobs:
        job.status = JobState.PENDING
        job.retry_count += 1

    db.commit()

    return stuck_jobs

def recover_stuck_queued_jobs(db, timeout_seconds=60, limit=None):
    if limit is None:
        limit = config_settings.RECOVER_STUCK_LIMIT
    
    threshold = datetime.utcnow() - timedelta(seconds=timeout_seconds)

    stmt = (
        select(Job)
        .where(
            Job.status == JobState.QUEUED,
            Job.queued_at < threshold
        )
        .order_by(Job.queued_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )

    result = db.execute(stmt)
    stuck_jobs = result.scalars().all()

    for job in stuck_jobs:
        job.status = JobState.PENDING
        job.retry_count += 1

    db.commit()

    return stuck_jobs