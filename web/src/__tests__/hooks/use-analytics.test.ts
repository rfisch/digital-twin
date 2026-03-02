import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useAnalytics } from "@/hooks/use-analytics";

vi.mock("@/lib/api", () => ({
  getBlogPosts: vi.fn(),
  invalidateAnalyticsCache: vi.fn(),
}));

import { getBlogPosts, invalidateAnalyticsCache } from "@/lib/api";

const mockGetBlogPosts = vi.mocked(getBlogPosts);
const mockInvalidateCache = vi.mocked(invalidateAnalyticsCache);

const mockPosts = [
  {
    title: "Test Post",
    path: "/test",
    url: "https://example.com/test",
    sessions: 50,
    views: 100,
    avg_duration: 120,
    revisit_ratio: 0.3,
    score: 85,
  },
];

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useAnalytics", () => {
  it("starts with empty blog posts", () => {
    const { result } = renderHook(() => useAnalytics());
    expect(result.current.blogPosts).toEqual([]);
    expect(result.current.isLoading).toBe(false);
  });

  it("fetchPosts calls API with correct params", async () => {
    mockGetBlogPosts.mockResolvedValueOnce(mockPosts);

    const { result } = renderHook(() => useAnalytics());

    await act(async () => {
      await result.current.fetchPosts(60, 10);
    });

    expect(mockGetBlogPosts).toHaveBeenCalledWith(60, 10);
    expect(result.current.blogPosts).toEqual(mockPosts);
  });

  it("refresh invalidates cache and re-fetches", async () => {
    mockGetBlogPosts.mockResolvedValue(mockPosts);
    mockInvalidateCache.mockResolvedValueOnce({ status: "ok" });

    const { result } = renderHook(() => useAnalytics());

    // First fetch
    await act(async () => {
      await result.current.fetchPosts(30, 20);
    });

    // Refresh
    await act(async () => {
      await result.current.refresh();
    });

    expect(mockInvalidateCache).toHaveBeenCalledOnce();
    // Should have called getBlogPosts twice (initial + refresh)
    expect(mockGetBlogPosts).toHaveBeenCalledTimes(2);
  });

  it("sets error on failure", async () => {
    mockGetBlogPosts.mockRejectedValueOnce(new Error("API error"));

    const { result } = renderHook(() => useAnalytics());

    await act(async () => {
      await result.current.fetchPosts();
    });

    expect(result.current.error).toBe("API error");
    expect(result.current.blogPosts).toEqual([]);
  });
});
