from datetime import datetime, timedelta
from sqlalchemy import func, and_

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

    running = db.query(func.count(Job.id)).filter(
        Job.status == JobState.RUNNING
    ).scalar()

    queued = db.query(func.count(Job.id)).filter(
        Job.status == JobState.QUEUED
    ).scalar()

    pending = db.query(func.count(Job.id)).filter(
        Job.status == JobState.PENDING
    ).scalar()

    # percentages
    success_rate = round((success / total) * 100, 2) if total else 0
    failure_rate = round((failed / total) * 100, 2) if total else 0

    # jobs retried
    retried_jobs = db.query(func.count(Job.id)).filter(
        Job.retry_count > 0
    ).scalar()

    # retried then succeeded
    recovered_jobs = db.query(func.count(Job.id)).filter(
        Job.retry_count > 0,
        Job.status == JobState.SUCCESS
    ).scalar()

    retry_recovery_rate = round(
        (recovered_jobs / retried_jobs) * 100, 2
    ) if retried_jobs else 0

    # avg queue wait time
    avg_wait = db.query(
        func.avg(
            func.extract(
                "epoch",
                Job.started_at - Job.queued_at
            )
        )
    ).filter(
        Job.started_at.isnot(None)
    ).scalar()

    avg_wait = round(avg_wait or 0, 2)

    # avg processing time
    avg_processing = db.query(
        func.avg(
            func.extract(
                "epoch",
                Job.updated_at - Job.started_at
            )
        )
    ).filter(
        Job.started_at.isnot(None),
        Job.updated_at.isnot(None),
        Job.status.in_([JobState.SUCCESS, JobState.FAILED])
    ).scalar()

    avg_processing = round(avg_processing or 0, 2)

    # throughput last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    processed_last_hour = db.query(func.count(Job.id)).filter(
        Job.updated_at >= one_hour_ago,
        Job.status.in_([JobState.SUCCESS, JobState.FAILED])
    ).scalar()

    throughput = round(processed_last_hour / 60, 2)

    return MetricResponse(
        total_jobs_processed=total,
        success_jobs=success,
        failed_jobs=failed,
        running_jobs=running,
        queued_jobs=queued,
        pending_jobs=pending,
        success_rate_percent=success_rate,
        failure_rate_percent=failure_rate,
        jobs_retried=retried_jobs,
        retry_recovery_rate_percent=retry_recovery_rate,
        avg_queue_wait_seconds=avg_wait,
        avg_processing_seconds=avg_processing,
        throughput_jobs_per_minute_last_hour=throughput,
    )