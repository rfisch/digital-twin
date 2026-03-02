"""LinkedIn endpoint — post directly to LinkedIn."""

import asyncio

from fastapi import APIRouter, HTTPException

from api import dependencies as deps
from api.schemas import PostLinkedInRequest, PostLinkedInResponse

router = APIRouter()


@router.post("/linkedin/post")
async def post_to_linkedin(req: PostLinkedInRequest) -> PostLinkedInResponse:
    if not deps.linkedin_client:
        raise HTTPException(status_code=503, detail="LinkedIn client not initialized")

    if not deps.linkedin_client.is_configured():
        raise HTTPException(status_code=404, detail="LinkedIn not configured")

    try:
        result = await asyncio.to_thread(deps.linkedin_client.create_post, req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return PostLinkedInResponse(**result)
