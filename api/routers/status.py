"""Status endpoint — service availability and model list."""

import asyncio

from fastapi import APIRouter

from api import dependencies as deps
from api.schemas import ServiceStatus

router = APIRouter()


@router.get("/status")
async def get_status() -> ServiceStatus:
    models = []
    ollama_available = False
    if deps.ollama_client:
        try:
            models = await asyncio.to_thread(deps.ollama_client.list_models)
            ollama_available = True
        except Exception:
            ollama_available = False

    return ServiceStatus(
        gmail_configured=deps.gmail_client.is_configured() if deps.gmail_client else False,
        linkedin_configured=deps.linkedin_client.is_configured() if deps.linkedin_client else False,
        analytics_configured=deps.analytics_client.is_configured() if deps.analytics_client else False,
        models=models,
        ollama_available=ollama_available,
    )
