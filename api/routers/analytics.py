"""Analytics endpoints — GA4 blog post data."""

import asyncio

from fastapi import APIRouter, HTTPException, Query

from api import dependencies as deps
from api.schemas import BlogPost

router = APIRouter()


@router.get("/analytics/blog-posts")
async def get_blog_posts(
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[BlogPost]:
    if not deps.analytics_client:
        raise HTTPException(status_code=503, detail="Analytics client not initialized")

    if not deps.analytics_client.is_configured():
        raise HTTPException(status_code=404, detail="Google Analytics not configured")

    try:
        results = await asyncio.to_thread(
            deps.analytics_client.get_top_blog_posts,
            days=days,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return [BlogPost(**r) for r in results]


@router.post("/analytics/invalidate-cache")
async def invalidate_cache():
    if not deps.analytics_client:
        raise HTTPException(status_code=503, detail="Analytics client not initialized")

    deps.analytics_client.invalidate_cache()
    return {"status": "ok"}
