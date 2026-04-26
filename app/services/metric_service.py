from sqlalchemy import func
from app.models.job import Job
from app.core.constants import JobState
from app.schemas.metric import MetricResponse


def get_metrics(db) -> MetricResponse:
    total = db.query(func.count(Job.id)).scalar()

    success = db.query(func.count(Job.id)).filter(
        Job.status == JobState.SUCCESS
    ).scalar()

    failed = db.query(func.count(Job.id)).filter(
        Job.status == JobState.FAILED
    ).scalar()

    pending = db.query(func.count(Job.id)).filter(
        Job.status == JobState.PENDING
    ).scalar()

    queued = db.query(func.count(Job.id)).filter(
        Job.status == JobState.QUEUED
    ).scalar()

    running = db.query(func.count(Job.id)).filter(
        Job.status == JobState.RUNNING
    ).scalar()

    success_rate = 0

    if total:
        success_rate = round((success / total) * 100, 2)

    return MetricResponse(
        total_jobs_processed=total,
        success_jobs=success,
        failed_jobs=failed,
        pending_jobs=pending,
        queued_jobs=queued,
        running_jobs=running,
        success_rate=success_rate,
    )