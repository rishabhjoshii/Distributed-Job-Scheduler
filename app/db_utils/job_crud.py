"""CRUD helpers for jobs."""
import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.config import config_settings
from app.core.constants import VALID_CANCELLABLE_JOB_STATES, JobState, normalize_value
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


def list_jobs(db: Session, status: str, limit: int, offset: int):
    status = normalize_value(status)

    if limit > 100: 
        limit = 100

    if offset < 0: 
        offset = 0
        
    query = db.query(Job)

    if status != "all":
        query = query.filter(Job.status == status)
        
    return (
        query
        .order_by(Job.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


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
        job.last_error = str(error)

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

    else:
        job.status = JobState.FAILED

    db.commit()
    return job

def claim_job(db, job_id):
    stmt = (
        select(Job)
        .where(
            Job.id == job_id,
            Job.status == JobState.QUEUED
        )
        .with_for_update(skip_locked=True)
    )

    job = db.execute(stmt).scalar_one_or_none()

    if not job:
        return None

    job.status = JobState.RUNNING
    job.started_at = datetime.utcnow()

    db.commit()
    return job

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

def retry_job(
    db,
    job_id,
    reset_retry_count=True,
    scheduled_at=None
):
    job = get_job(db, job_id)

    if not job:
        return None

    if job.status != "failed":
        raise ValueError(
            "Only failed jobs can be retried"
        )

    job.status = "pending"
    job.last_error = None
    job.started_at = None
    job.queued_at = None

    job.scheduled_at = (
        scheduled_at or datetime.utcnow()
    )

    if reset_retry_count:
        job.retry_count = 0

    db.commit()
    db.refresh(job)

    return job

def cancel_job(db, job_id):
    job = get_job(db, job_id)

    if not job:
        return None

    if job.status not in VALID_CANCELLABLE_JOB_STATES:
        raise ValueError(
            f"Cannot cancel job in state {job.status}"
        )

    job.status = JobState.CANCELLED

    db.commit()
    db.refresh(job)

    return job

def get_job_metrics(db: Session):
    total = db.query(func.count(Job.id)).scalar() or 0

    success = db.query(func.count(Job.id)).filter(Job.status == "success").scalar() or 0
    failed = db.query(func.count(Job.id)).filter(Job.status == "failed").scalar() or 0
    running = db.query(func.count(Job.id)).filter(Job.status == "running").scalar() or 0
    queued = db.query(func.count(Job.id)).filter(Job.status == "queued").scalar() or 0
    pending = db.query(func.count(Job.id)).filter(Job.status == "pending").scalar() or 0

    jobs_retried = db.query(func.count(Job.id)).filter(Job.retry_count > 0).scalar() or 0

    recovered = db.query(func.count(Job.id)).filter(
        Job.retry_count > 0,
        Job.status == "success"
    ).scalar() or 0

    avg_queue_wait = db.query(
        func.avg(func.extract("epoch", Job.started_at - Job.queued_at))
    ).filter(
        Job.started_at.isnot(None),
        Job.queued_at.isnot(None)
    ).scalar() or 0

    avg_processing = db.query(
        func.avg(func.extract("epoch", Job.updated_at - Job.started_at))
    ).filter(
        Job.started_at.isnot(None),
        Job.updated_at.isnot(None)
    ).scalar() or 0

    first_job = db.query(Job).order_by(Job.created_at.asc()).first()
    last_job = db.query(Job).order_by(Job.created_at.desc()).first()

    throughput = 0

    if first_job and last_job and first_job.created_at != last_job.created_at:
        elapsed_seconds = (
            last_job.created_at - first_job.created_at
        ).total_seconds()

        elapsed_minutes = elapsed_seconds / 60

        if elapsed_minutes > 0:
            throughput = total / elapsed_minutes

    success_rate = (success / total * 100) if total > 0 else 0
    failure_rate = (failed / total * 100) if total > 0 else 0
    retry_recovery = (recovered / jobs_retried * 100) if jobs_retried > 0 else 0

    return {
        "total_jobs_processed": total,
        "success_jobs": success,
        "failed_jobs": failed,
        "running_jobs": running,
        "queued_jobs": queued,
        "pending_jobs": pending,
        "success_rate_percent": round(success_rate, 2),
        "failure_rate_percent": round(failure_rate, 2),
        "jobs_retried": jobs_retried,
        "retry_recovery_rate_percent": round(retry_recovery, 2),
        "avg_queue_wait_seconds": round(avg_queue_wait, 2),
        "avg_processing_seconds": round(avg_processing, 2),
        "throughput_jobs_per_minute_last_hour": round(throughput, 2),
    }
