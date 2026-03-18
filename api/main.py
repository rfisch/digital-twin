"""FastAPI application — thin REST wrapper around existing Python modules."""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# ─── Request logger ────────────────────────────────────────────────
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

request_logger = logging.getLogger("api.requests")
request_logger.setLevel(logging.INFO)
_handler = logging.FileHandler(LOG_DIR / "api.log")
_handler.setFormatter(logging.Formatter("%(asctime)s\t%(message)s"))
request_logger.addHandler(_handler)

from api import dependencies as deps
from api.routers import status, generate, analytics, scheduler, linkedin, gmail, feedback
from app.assistant import WritingAssistant
from app.analytics_client import AnalyticsClient
from app.scheduler import PostScheduler
from app.linkedin_client import LinkedInClient
from app.gmail_client import GmailClient
from app.feedback_store import FeedbackStore
from app.ollama_client import OllamaClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: instantiate all singletons
    deps.assistant = WritingAssistant()
    deps.analytics_client = AnalyticsClient()
    deps.scheduler = PostScheduler()
    deps.linkedin_client = LinkedInClient()
    deps.gmail_client = GmailClient()
    deps.feedback_store = FeedbackStore()
    deps.ollama_client = OllamaClient()
    yield
    # Shutdown: stop Ollama if it was started
    if deps.assistant:
        deps.assistant.shutdown()


app = FastAPI(title="Jacq's Writing Assistant API", lifespan=lifespan)

# CORS — allow any origin (single-user local tool, accessed via LAN)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request logging middleware ────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed_ms = (time.time() - start) * 1000
    request_logger.info(
        "%s %s %s %.0fms %s",
        request.client.host if request.client else "-",
        request.method,
        request.url.path,
        elapsed_ms,
        response.status_code,
    )
    return response


# Register routers
app.include_router(status.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(scheduler.router, prefix="/api")
app.include_router(linkedin.router, prefix="/api")
app.include_router(gmail.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
