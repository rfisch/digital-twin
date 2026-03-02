import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  getStatus,
  generate,
  generateLinkedInMulti,
  getBlogPosts,
  invalidateAnalyticsCache,
  getScheduledPosts,
  schedulePost,
  cancelScheduledPost,
  reschedulePost,
  postToLinkedIn,
  sendEmail,
  saveFeedback,
  ApiError,
} from "@/lib/api";

const mockFetch = vi.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
});

function mockOk(data: unknown) {
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve(data),
  });
}

function mockError(status: number, detail: string) {
  mockFetch.mockResolvedValueOnce({
    ok: false,
    status,
    statusText: "Error",
    json: () => Promise.resolve({ detail }),
  });
}

describe("getStatus", () => {
  it("fetches /api/status", async () => {
    const data = {
      gmail_configured: true,
      linkedin_configured: false,
      analytics_configured: true,
      models: ["jacq-v6:8b"],
      ollama_available: true,
    };
    mockOk(data);
    const result = await getStatus();
    expect(result).toEqual(data);
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/status",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } }),
    );
  });
});

describe("generate", () => {
  it("posts to /api/generate", async () => {
    mockOk({ text: "Hello", prompt_info: { system: "s", user: "u" } });
    const result = await generate({
      task_type: "blog",
      topic: "test",
      model: "jacq-v6:8b",
      temperature: 0.7,
      max_tokens: 2048,
      use_rag: false,
    });
    expect(result.text).toBe("Hello");
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/generate",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("generateLinkedInMulti", () => {
  it("posts to /api/generate/linkedin", async () => {
    mockOk({
      posts: [
        { text: "Post 1", prompt_info: null },
        { text: "Post 2", prompt_info: null },
      ],
    });
    const result = await generateLinkedInMulti({
      blog_url: "https://example.com",
      count: 2,
      model: "jacq-v6:8b",
      temperature: 0.6,
      max_tokens: 512,
    });
    expect(result.posts).toHaveLength(2);
  });
});

describe("getBlogPosts", () => {
  it("fetches with days and limit params", async () => {
    mockOk([{ title: "Post", url: "https://example.com", views: 100 }]);
    await getBlogPosts(60, 10);
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/analytics/blog-posts?days=60&limit=10",
      expect.anything(),
    );
  });
});

describe("invalidateAnalyticsCache", () => {
  it("posts to invalidate-cache", async () => {
    mockOk({ status: "ok" });
    await invalidateAnalyticsCache();
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/analytics/invalidate-cache",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("schedulePost", () => {
  it("posts to /api/schedule", async () => {
    mockOk({ id: "abc123" });
    const result = await schedulePost({
      content: "test post",
      scheduled_at: "2026-03-01T12:00:00Z",
    });
    expect(result.id).toBe("abc123");
  });
});

describe("cancelScheduledPost", () => {
  it("sends DELETE", async () => {
    mockOk({ status: "ok" });
    await cancelScheduledPost("abc123");
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/schedule/abc123",
      expect.objectContaining({ method: "DELETE" }),
    );
  });
});

describe("reschedulePost", () => {
  it("sends PATCH", async () => {
    mockOk({ status: "ok" });
    await reschedulePost("abc123", "2026-03-02T12:00:00Z");
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/schedule/abc123",
      expect.objectContaining({ method: "PATCH" }),
    );
  });
});

describe("postToLinkedIn", () => {
  it("posts text to linkedin", async () => {
    mockOk({ success: true, message: "Posted" });
    const result = await postToLinkedIn("hello linkedin");
    expect(result.success).toBe(true);
  });
});

describe("sendEmail", () => {
  it("sends email", async () => {
    mockOk({ success: true, message: "Sent", message_id: "123" });
    const result = await sendEmail("to@example.com", "Subject", "<p>body</p>");
    expect(result.success).toBe(true);
  });
});

describe("saveFeedback", () => {
  it("saves feedback record", async () => {
    mockOk({ id: "feedback-123" });
    const result = await saveFeedback({
      task_type: "blog",
      model: "jacq-v6:8b",
      temperature: 0.7,
      prompt: "test",
      original_output: "original",
      edited_output: "edited",
      was_edited: true,
      was_sent: false,
    });
    expect(result.id).toBe("feedback-123");
  });
});

describe("error handling", () => {
  it("throws ApiError on non-ok response", async () => {
    mockError(422, "Validation failed");
    await expect(getStatus()).rejects.toThrow(ApiError);
  });

  it("includes status and detail", async () => {
    mockError(500, "Internal error");
    try {
      await getStatus();
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).status).toBe(500);
      expect((e as ApiError).detail).toBe("Internal error");
    }
  });
});
