"""Scheduler endpoints — schedule, list, cancel, reschedule posts."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from api import dependencies as deps
from api.schemas import (
    ScheduleRequest,
    ScheduleResponse,
    RescheduleRequest,
    ScheduledPost,
)

router = APIRouter()


def _parse_iso(dt_str: str) -> float:
    """Parse ISO 8601 string to Unix timestamp."""
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid datetime: {dt_str}")


@router.get("/schedule")
async def get_pending() -> list[ScheduledPost]:
    if not deps.scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")

    posts = deps.scheduler.get_pending()
    return [ScheduledPost(**p) for p in posts]


@router.post("/schedule")
async def schedule_post(req: ScheduleRequest) -> ScheduleResponse:
    if not deps.scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")

    ts = _parse_iso(req.scheduled_at)
    schedule_id = deps.scheduler.schedule(
        content=req.content,
        scheduled_at=ts,
        source_url=req.source_url,
        feedback_id=req.feedback_id,
    )
    return ScheduleResponse(id=schedule_id)


@router.delete("/schedule/{schedule_id}")
async def cancel_post(schedule_id: str):
    if not deps.scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")

    try:
        deps.scheduler.cancel(schedule_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok"}


@router.patch("/schedule/{schedule_id}")
async def reschedule_post(schedule_id: str, req: RescheduleRequest):
    if not deps.scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")

    ts = _parse_iso(req.new_time)
    try:
        deps.scheduler.reschedule(schedule_id, ts)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok"}
