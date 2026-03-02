/**
 * Typed fetch wrapper for all API endpoints.
 */

import type {
  GenerateRequest,
  GenerateResponse,
  LinkedInMultiRequest,
  LinkedInMultiResponse,
  ServiceStatus,
  BlogPost,
  ScheduledPost,
  ScheduleRequest,
  FeedbackRequest,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore JSON parse errors
    }
    throw new ApiError(res.status, detail);
  }

  return res.json() as Promise<T>;
}

// --- Status ---

export function getStatus(): Promise<ServiceStatus> {
  return request<ServiceStatus>("/api/status");
}

// --- Generation ---

export function generate(req: GenerateRequest): Promise<GenerateResponse> {
  return request<GenerateResponse>("/api/generate", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function generateLinkedInMulti(req: LinkedInMultiRequest): Promise<LinkedInMultiResponse> {
  return request<LinkedInMultiResponse>("/api/generate/linkedin", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

// --- Analytics ---

export function getBlogPosts(days = 30, limit = 20): Promise<BlogPost[]> {
  return request<BlogPost[]>(`/api/analytics/blog-posts?days=${days}&limit=${limit}`);
}

export function invalidateAnalyticsCache(): Promise<{ status: string }> {
  return request<{ status: string }>("/api/analytics/invalidate-cache", {
    method: "POST",
  });
}

// --- Scheduler ---

export function getScheduledPosts(): Promise<ScheduledPost[]> {
  return request<ScheduledPost[]>("/api/schedule");
}

export function schedulePost(req: ScheduleRequest): Promise<{ id: string }> {
  return request<{ id: string }>("/api/schedule", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function cancelScheduledPost(id: string): Promise<{ status: string }> {
  return request<{ status: string }>(`/api/schedule/${id}`, {
    method: "DELETE",
  });
}

export function reschedulePost(id: string, newTime: string): Promise<{ status: string }> {
  return request<{ status: string }>(`/api/schedule/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ new_time: newTime }),
  });
}

// --- LinkedIn ---

export function postToLinkedIn(text: string): Promise<{ success: boolean; message: string }> {
  return request<{ success: boolean; message: string }>("/api/linkedin/post", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

// --- Gmail ---

export function sendEmail(
  to: string,
  subject: string,
  htmlBody: string,
): Promise<{ success: boolean; message: string; message_id: string | null }> {
  return request<{ success: boolean; message: string; message_id: string | null }>(
    "/api/gmail/send",
    {
      method: "POST",
      body: JSON.stringify({ to, subject, html_body: htmlBody }),
    },
  );
}

// --- Feedback ---

export function saveFeedback(req: FeedbackRequest): Promise<{ id: string }> {
  return request<{ id: string }>("/api/feedback", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export { ApiError };
