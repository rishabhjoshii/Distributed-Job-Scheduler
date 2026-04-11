"""CRUD helpers for jobs."""
from sqlalchemy.orm import Session
from datetime import datetime
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
    return db.query(Job).filter(Job.id == job_id).first()


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