"""Gmail endpoint — send email."""

import asyncio

from fastapi import APIRouter, HTTPException

from api import dependencies as deps
from api.schemas import SendEmailRequest, SendEmailResponse

router = APIRouter()


@router.post("/gmail/send")
async def send_email(req: SendEmailRequest) -> SendEmailResponse:
    if not deps.gmail_client:
        raise HTTPException(status_code=503, detail="Gmail client not initialized")

    if not deps.gmail_client.is_configured():
        raise HTTPException(status_code=404, detail="Gmail not configured")

    try:
        result = await asyncio.to_thread(
            deps.gmail_client.send_email, req.to, req.subject, req.html_body
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return SendEmailResponse(**result)
