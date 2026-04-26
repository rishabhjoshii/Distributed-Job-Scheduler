"""Job service layer."""
from sqlalchemy.orm import Session
from app.db_utils import job_crud


def create_job(db: Session, job_data):
    return job_crud.create_job(db, job_data)


def get_job(db: Session, job_id):
    return job_crud.get_job(db, job_id)


def list_jobs(db: Session, status: str):
    return job_crud.list_jobs(db, status)

def retry_job(
    db,
    job_id,
    reset_retry_count=True,
    scheduled_at=None
):
    return job_crud.retry_job(
        db,
        job_id,
        reset_retry_count,
        scheduled_at
    )

def cancel_job(db, job_id):
    return job_crud.cancel_job(db, job_id)