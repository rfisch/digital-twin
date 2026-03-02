import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useScheduler } from "@/hooks/use-scheduler";

vi.mock("@/lib/api", () => ({
  getScheduledPosts: vi.fn(),
  schedulePost: vi.fn(),
  cancelScheduledPost: vi.fn(),
  reschedulePost: vi.fn(),
}));

import {
  getScheduledPosts,
  schedulePost,
  cancelScheduledPost,
  reschedulePost,
} from "@/lib/api";

const mockGetPosts = vi.mocked(getScheduledPosts);
const mockSchedule = vi.mocked(schedulePost);
const mockCancel = vi.mocked(cancelScheduledPost);
const mockReschedule = vi.mocked(reschedulePost);

const mockPost = {
  id: "abc123",
  content: "Test post",
  scheduled_at: 1709308800,
  created_at: 1709222400,
  status: "pending",
  posted_at: null,
  error: null,
  source_url: "",
  feedback_id: "",
};

beforeEach(() => {
  vi.clearAllMocks();
  mockGetPosts.mockResolvedValue([]);
});

describe("useScheduler", () => {
  it("starts with empty posts", () => {
    const { result } = renderHook(() => useScheduler());
    expect(result.current.posts).toEqual([]);
  });

  it("refresh fetches pending posts", async () => {
    mockGetPosts.mockResolvedValueOnce([mockPost]);

    const { result } = renderHook(() => useScheduler());

    await act(async () => {
      await result.current.refresh();
    });

    expect(result.current.posts).toEqual([mockPost]);
  });

  it("schedule creates post and refreshes", async () => {
    mockSchedule.mockResolvedValueOnce({ id: "new-id" });

    const { result } = renderHook(() => useScheduler());

    let id: string | null = null;
    await act(async () => {
      id = await result.current.schedule(
        "content",
        "2026-03-01T12:00:00Z",
        "https://example.com",
      );
    });

    expect(id).toBe("new-id");
    expect(mockSchedule).toHaveBeenCalledWith({
      content: "content",
      scheduled_at: "2026-03-01T12:00:00Z",
      source_url: "https://example.com",
      feedback_id: "",
    });
  });

  it("cancel removes post and refreshes", async () => {
    mockCancel.mockResolvedValueOnce({ status: "ok" });

    const { result } = renderHook(() => useScheduler());

    let success: boolean;
    await act(async () => {
      success = await result.current.cancel("abc123");
    });

    expect(success!).toBe(true);
    expect(mockCancel).toHaveBeenCalledWith("abc123");
  });

  it("reschedule updates post time", async () => {
    mockReschedule.mockResolvedValueOnce({ status: "ok" });

    const { result } = renderHook(() => useScheduler());

    let success: boolean;
    await act(async () => {
      success = await result.current.reschedule("abc123", "2026-03-02T12:00:00Z");
    });

    expect(success!).toBe(true);
    expect(mockReschedule).toHaveBeenCalledWith("abc123", "2026-03-02T12:00:00Z");
  });

  it("sets error on failure", async () => {
    mockSchedule.mockRejectedValueOnce(new Error("Schedule failed"));

    const { result } = renderHook(() => useScheduler());

    await act(async () => {
      const id = await result.current.schedule("content", "2026-03-01T12:00:00Z");
      expect(id).toBeNull();
    });

    expect(result.current.error).toBe("Schedule failed");
  });
});
