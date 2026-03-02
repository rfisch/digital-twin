"""Generation endpoints — single and LinkedIn multi-post."""

import asyncio

from fastapi import APIRouter, HTTPException

from api import dependencies as deps
from api.schemas import (
    GenerateRequest,
    GenerateResponse,
    LinkedInMultiRequest,
    LinkedInMultiResponse,
    PromptInfo,
)

router = APIRouter()


@router.post("/generate")
async def generate(req: GenerateRequest) -> GenerateResponse:
    if not deps.assistant:
        raise HTTPException(status_code=503, detail="Assistant not initialized")

    # Build kwargs for task-specific fields
    kwargs = {}
    if req.task_type == "email":
        kwargs.update(recipient=req.recipient, purpose=req.purpose, email_type=req.email_type)
    elif req.task_type == "email_reply":
        if not req.received_email:
            raise HTTPException(status_code=422, detail="received_email is required for email_reply")
        kwargs.update(
            received_email=req.received_email,
            sender_name=req.sender_name,
            sender_email=req.sender_email,
            subject=req.subject,
            goal=req.goal,
            tone_notes=req.tone_notes,
        )
    elif req.task_type == "copywriting":
        kwargs.update(medium=req.medium, audience=req.audience, message=req.message, tone=req.tone)

    # Validate topic for non-LinkedIn, non-email-reply tasks
    if req.task_type not in ("linkedin", "email_reply") and not req.topic:
        raise HTTPException(status_code=422, detail="topic is required")

    try:
        result = await asyncio.to_thread(
            deps.assistant.generate,
            task_type=req.task_type,
            topic=req.topic,
            use_rag=req.use_rag,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            return_prompt=True,
            **kwargs,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # generate() with return_prompt=True returns (text, prompt_dict)
    text, prompt_dict = result
    return GenerateResponse(
        text=text,
        prompt_info=PromptInfo(
            system=prompt_dict.get("system", ""),
            user=prompt_dict.get("user", ""),
        ),
    )


@router.post("/generate/linkedin")
async def generate_linkedin_multi(req: LinkedInMultiRequest) -> LinkedInMultiResponse:
    if not deps.assistant:
        raise HTTPException(status_code=503, detail="Assistant not initialized")

    if not req.blog_url:
        raise HTTPException(status_code=422, detail="blog_url is required")

    try:
        results = await asyncio.to_thread(
            deps.assistant.generate_linkedin_multi,
            url=req.blog_url,
            count=req.count,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    posts = [
        GenerateResponse(
            text=r["text"],
            prompt_info=PromptInfo(
                system=r.get("prompt_info", {}).get("system", ""),
                user=r.get("prompt_info", {}).get("user", ""),
            ),
        )
        for r in results
    ]
    return LinkedInMultiResponse(posts=posts)
