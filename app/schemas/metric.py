from pydantic import BaseModel

class MetricResponse(BaseModel):
    jobs_processed: int
    jobs_failed: int
    jobs_retried: int
