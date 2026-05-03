"""Job API routes."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.constants import JobStatusFilter, normalize_status_filter, validate_create_job_request_payload
from app.db.session import get_db
from app.schemas.job import JobCreate, JobResponse, RetryJobRequest
from app.services import job_service

router = APIRouter()


@router.post("/jobs", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    try:
        validated_payload = validate_create_job_request_payload(job.type, job.payload)
        job.payload = validated_payload.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid payload for job type '{job.type}': {e}"
        )

    return job_service.create_job(db, job)


@router.get("/jobs", response_model=List[JobResponse])
def list_jobs(
    status: JobStatusFilter = Query(
        "all",
        description="Filter by status: pending, running, queued, success, failed, or all.",
    ),
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    try:
        normalized_status = normalize_status_filter(status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return job_service.list_jobs(db, normalized_status, limit, offset)


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/jobs/{job_id}/retry", response_model=JobResponse)
def retry_job(
    job_id: str,
    request: RetryJobRequest,
    db: Session = Depends(get_db)
):
    try:
        job = job_service.retry_job(
            db=db,
            job_id=job_id,
            reset_retry_count=request.reset_retry_count,
            scheduled_at=request.scheduled_at
        )

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        return job

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc


@router.post("/jobs/{job_id}/cancel", response_model=JobResponse)
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    try:
        job = job_service.cancel_job(db, job_id)

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        return job

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc