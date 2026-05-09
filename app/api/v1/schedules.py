from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.constants import ScheduleStatus, ValidJobTypes
from app.core.payloads import normalize_payload_dict
from app.db.session import get_db
from app.schemas.schedule import ScheduleCreate, ScheduleResponse
from app.services import schedule_service
from app.services.schedule_service import create_schedule


router = APIRouter()


@router.post("/schedules")
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    try:
        schedule.payload = normalize_payload_dict(schedule.type, schedule.payload)
        return schedule_service.create_schedule(db, schedule)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/schedules", response_model=list[ScheduleResponse])
def list_schedules(
    status: ScheduleStatus = Query(
        ScheduleStatus.ALL,
        description="Filter by status: All, Active, Inactive.",
    ),
    # type: ValidJobTypes = Query(
    #     "all",
    #     description="Filter by Type: Webhook, Email, Log",
    # ),
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    return schedule_service.list_schedules(db, status, limit, offset)

@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(schedule_id: str, db: Session = Depends(get_db)):
    schedule = schedule_service.get_schedule(db, schedule_id)

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return schedule

@router.post("/schedules/{schedule_id}/cancel")
def cancel_schedule(schedule_id: str, db: Session = Depends(get_db)):
    schedule = schedule_service.cancel_schedule(db, schedule_id)

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return {"message": "Schedule cancelled"}
