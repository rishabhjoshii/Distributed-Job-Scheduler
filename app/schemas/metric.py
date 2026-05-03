from pydantic import BaseModel


class MetricResponse(BaseModel):
    # Job metrics
    total_jobs_processed: int
    success_jobs: int
    failed_jobs: int
    running_jobs: int
    queued_jobs: int
    pending_jobs: int

    success_rate_percent: float
    failure_rate_percent: float

    jobs_retried: int
    retry_recovery_rate_percent: float

    avg_queue_wait_seconds: float
    avg_processing_seconds: float

    throughput_jobs_per_minute_last_hour: float

    # Schedule metrics
    total_schedules: int
    active_schedules: int
    inactive_schedules: int
    avg_runs_per_schedule: float