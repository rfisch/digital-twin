"""FastAPI application — thin REST wrapper around existing Python modules."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# CORS for Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7860", "https://localhost:7860"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(status.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(scheduler.router, prefix="/api")
app.include_router(linkedin.router, prefix="/api")
app.include_router(gmail.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
