"""Feedback endpoint — save edit records."""

from fastapi import APIRouter, HTTPException

from api import dependencies as deps
from api.schemas import FeedbackRequest, FeedbackResponse

router = APIRouter()


@router.post("/feedback")
async def save_feedback(req: FeedbackRequest) -> FeedbackResponse:
    if not deps.feedback_store:
        raise HTTPException(status_code=503, detail="Feedback store not initialized")

    record = {
        "task_type": req.task_type,
        "model": req.model,
        "temperature": req.temperature,
        "prompt": req.prompt,
        "original_output": req.original_output,
        "edited_output": req.edited_output,
        "was_edited": req.was_edited,
        "was_sent": req.was_sent,
        "metadata": req.metadata,
    }

    try:
        record_id = deps.feedback_store.save(record)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FeedbackResponse(id=record_id)
