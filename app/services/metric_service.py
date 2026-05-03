from app.db_utils import job_crud, schedule_crud
from app.schemas.metric import MetricResponse


def get_metrics(db) -> MetricResponse:
    job_metrics = job_crud.get_job_metrics(db)
    schedule_metrics = schedule_crud.get_schedule_metrics(db)

    return {
        **job_metrics,
        **schedule_metrics
    }