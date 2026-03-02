"""Pydantic request/response models for the API."""

from pydantic import BaseModel, Field


# --- Requests ---


class GenerateRequest(BaseModel):
    task_type: str = Field(description="One of: blog, email, email_reply, copywriting, linkedin, freeform")
    topic: str = ""
    model: str = "jacq-v6:8b"
    temperature: float = 0.7
    max_tokens: int = 2048
    use_rag: bool = False
    # Email fields
    recipient: str = ""
    purpose: str = ""
    email_type: str = ""
    # Email reply fields
    received_email: str = ""
    sender_name: str = ""
    sender_email: str = ""
    subject: str = ""
    goal: str = ""
    tone_notes: str = ""
    # Copywriting fields
    medium: str = ""
    audience: str = ""
    message: str = ""
    tone: str = ""


class LinkedInMultiRequest(BaseModel):
    blog_url: str
    count: int = Field(default=3, ge=1, le=5)
    model: str = "jacq-v6:8b"
    temperature: float = 0.6
    max_tokens: int = 512


class ScheduleRequest(BaseModel):
    content: str
    scheduled_at: str = Field(description="ISO 8601 datetime string")
    source_url: str = ""
    feedback_id: str = ""


class RescheduleRequest(BaseModel):
    new_time: str = Field(description="ISO 8601 datetime string")


class FeedbackRequest(BaseModel):
    task_type: str
    model: str = ""
    temperature: float = 0.7
    prompt: str = ""
    original_output: str = ""
    edited_output: str = ""
    was_edited: bool = False
    was_sent: bool = False
    metadata: dict = Field(default_factory=dict)


class PostLinkedInRequest(BaseModel):
    text: str


class SendEmailRequest(BaseModel):
    to: str
    subject: str
    html_body: str


# --- Responses ---


class PromptInfo(BaseModel):
    system: str = ""
    user: str = ""


class GenerateResponse(BaseModel):
    text: str
    prompt_info: PromptInfo | None = None


class LinkedInMultiResponse(BaseModel):
    posts: list[GenerateResponse]


class ServiceStatus(BaseModel):
    gmail_configured: bool = False
    linkedin_configured: bool = False
    analytics_configured: bool = False
    models: list[str] = Field(default_factory=list)
    ollama_available: bool = False


class ScheduledPost(BaseModel):
    id: str
    content: str
    scheduled_at: float
    created_at: float
    status: str
    posted_at: float | None = None
    error: str | None = None
    source_url: str = ""
    feedback_id: str = ""


class ScheduleResponse(BaseModel):
    id: str


class FeedbackResponse(BaseModel):
    id: str


class PostLinkedInResponse(BaseModel):
    success: bool
    message: str


class SendEmailResponse(BaseModel):
    success: bool
    message: str
    message_id: str | None = None


class BlogPost(BaseModel):
    title: str
    path: str
    url: str
    sessions: int
    views: int
    avg_duration: float
    revisit_ratio: float
    score: float
