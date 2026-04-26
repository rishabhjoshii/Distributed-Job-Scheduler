from pydantic import BaseModel

class MetricResponse(BaseModel):
    total_jobs_processed: int
    success_jobs: int
    failed_jobs: int
    pending_jobs: int
    queued_jobs: int
    running_jobs: int
    success_rate: float

