"""CRUD helpers for jobs."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.constants import JobState
from app.models.job import Job


def create_job(db: Session, job_data):
    job = Job(
        type=job_data.type,
        payload=job_data.payload,
        scheduled_at=job_data.scheduled_at or datetime.utcnow(),
        max_retries=job_data.max_retries or 3
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
    job.max_retries = job_data.max_retries or 3

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
            Job.status == "pending",
            Job.scheduled_at <= datetime.utcnow()
        )
        .order_by(Job.scheduled_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )

    result = db.execute(query)
    jobs = result.scalars().all()

    db.commit()
    return jobs

def update_job_status(db: Session, job_id, status, error=None):
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
        delay_seconds = 2 ** job.retry_count

        job.status = "pending"
        job.scheduled_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        job.retry_count += 1

        print(f"Job {job_id} re-scheduled for {str(job.scheduled_at)}")

    else:
        job.status = "failed"

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

def recover_stuck_jobs(db, timeout_seconds=60, limit=50):
    threshold = datetime.utcnow() - timedelta(seconds=timeout_seconds)

    stmt = (
        select(Job)
        .where(
            Job.status == JobState.RUNNING,
            Job.started_at < threshold
        )
        .order_by(Job.started_at)
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