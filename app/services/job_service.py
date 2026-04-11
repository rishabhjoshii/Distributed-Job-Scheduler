"""Job service layer."""
from sqlalchemy.orm import Session
from app.db_utils import job_crud


def create_job(db: Session, job_data):
    return job_crud.create_job(db, job_data)


def get_job(db: Session, job_id):
    return job_crud.get_job(db, job_id)