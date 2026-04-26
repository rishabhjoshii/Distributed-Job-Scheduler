from fastapi import APIRouter
from app.schemas.metric import MetricResponse
from app.services import metric_service

router = APIRouter()

@router.get("/metrics", response_model=MetricResponse)
def get_metrics():
    return metric_service.get_metrics()