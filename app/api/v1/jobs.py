"""Job API routes."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.constants import JobStatusFilter, normalize_status_filter
from app.db.session import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services import job_service

router = APIRouter()


@router.post("/jobs", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    return job_service.create_job(db, job)


@router.get("/jobs", response_model=List[JobResponse])
def list_jobs(
    status: JobStatusFilter = Query(
        "all",
        description="Filter by status: pending, running, queued, success, failed, or all.",
    ),
    db: Session = Depends(get_db),
):
    try:
        normalized_status = normalize_status_filter(status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return job_service.list_jobs(db, normalized_status)


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job