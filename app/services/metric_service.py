
from app.core.metrics import metrics
from app.schemas.metric import MetricResponse


def get_metrics() -> MetricResponse:
    return MetricResponse(
        jobs_processed=metrics.jobs_processed,
        jobs_failed=metrics.jobs_failed,
        jobs_retried=metrics.jobs_retried
    )