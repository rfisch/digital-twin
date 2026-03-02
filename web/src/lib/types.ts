export type TaskType = "blog" | "email" | "email_reply" | "copywriting" | "linkedin" | "freeform";

export const TASK_LABELS: Record<TaskType, string> = {
  blog: "Blog Post",
  email: "Email",
  email_reply: "Email Reply",
  copywriting: "Copywriting",
  linkedin: "LinkedIn Post",
  freeform: "Freeform",
};

export const TASK_DEFAULTS: Record<TaskType, { temperature: number; maxTokens: number }> = {
  blog: { temperature: 0.7, maxTokens: 2048 },
  email: { temperature: 0.7, maxTokens: 2048 },
  email_reply: { temperature: 0.7, maxTokens: 2048 },
  copywriting: { temperature: 0.7, maxTokens: 2048 },
  linkedin: { temperature: 0.6, maxTokens: 512 },
  freeform: { temperature: 0.7, maxTokens: 2048 },
};

export interface PromptInfo {
  system: string;
  user: string;
}

export interface GenerateResponse {
  text: string;
  prompt_info: PromptInfo | null;
}

export interface LinkedInMultiResponse {
  posts: GenerateResponse[];
}

export interface ServiceStatus {
  gmail_configured: boolean;
  linkedin_configured: boolean;
  analytics_configured: boolean;
  models: string[];
  ollama_available: boolean;
}

export interface BlogPost {
  title: string;
  path: string;
  url: string;
  sessions: number;
  views: number;
  avg_duration: number;
  revisit_ratio: number;
  score: number;
}

export interface ScheduledPost {
  id: string;
  content: string;
  scheduled_at: number;
  created_at: number;
  status: string;
  posted_at: number | null;
  error: string | null;
  source_url: string;
  feedback_id: string;
}

export interface GenerateRequest {
  task_type: TaskType;
  topic: string;
  model: string;
  temperature: number;
  max_tokens: number;
  use_rag: boolean;
  // Email fields
  recipient?: string;
  purpose?: string;
  email_type?: string;
  // Email reply fields
  received_email?: string;
  sender_name?: string;
  sender_email?: string;
  subject?: string;
  goal?: string;
  tone_notes?: string;
  // Copywriting fields
  medium?: string;
  audience?: string;
  message?: string;
  tone?: string;
}

export interface LinkedInMultiRequest {
  blog_url: string;
  count: number;
  model: string;
  temperature: number;
  max_tokens: number;
}

export interface ScheduleRequest {
  content: string;
  scheduled_at: string;
  source_url?: string;
  feedback_id?: string;
}

export interface FeedbackRequest {
  task_type: string;
  model: string;
  temperature: number;
  prompt: string;
  original_output: string;
  edited_output: string;
  was_edited: boolean;
  was_sent: boolean;
  metadata?: Record<string, unknown>;
}

export interface EmailFields {
  recipient: string;
  purpose: string;
  emailType: string;
}

export interface EmailReplyFields {
  receivedEmail: string;
  senderName: string;
  senderEmail: string;
  subject: string;
  goal: string;
  toneNotes: string;
}

export interface CopywritingFields {
  medium: string;
  audience: string;
  message: string;
  tone: string;
}

export interface LinkedInFields {
  blogUrl: string;
  postCount: number;
  timeRange: number;
}

export interface PostResult {
  text: string;
  originalText: string;
  promptInfo: PromptInfo | null;
}
