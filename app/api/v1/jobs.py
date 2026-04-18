"""Job API routes."""
from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.job import JobCreate, JobResponse
from app.services import job_service
from app.db.session import SessionLocal

router = APIRouter()

JobStatusFilter = Literal["all", "pending", "running", "success", "failed"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/jobs", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    return job_service.create_job(db, job)


@router.get("/jobs", response_model=List[JobResponse])
def list_jobs(
    status: JobStatusFilter = Query(
        "all",
        description="Filter by status: pending, running, success, failed, or all.",
    ),
    db: Session = Depends(get_db),
):
    return job_service.list_jobs(db, status)


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job