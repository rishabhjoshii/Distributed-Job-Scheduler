from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.schemas.metric import MetricResponse
from app.services import metric_service
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/metrics", response_model=MetricResponse)
def get_metrics(db: Session = Depends(get_db)):
    return metric_service.get_metrics(db)