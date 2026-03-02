"""Shared singleton instances initialized by the app lifespan."""

from app.assistant import WritingAssistant
from app.analytics_client import AnalyticsClient
from app.scheduler import PostScheduler
from app.linkedin_client import LinkedInClient
from app.gmail_client import GmailClient
from app.feedback_store import FeedbackStore
from app.ollama_client import OllamaClient

assistant: WritingAssistant | None = None
analytics_client: AnalyticsClient | None = None
scheduler: PostScheduler | None = None
linkedin_client: LinkedInClient | None = None
gmail_client: GmailClient | None = None
feedback_store: FeedbackStore | None = None
ollama_client: OllamaClient | None = None
