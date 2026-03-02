"use client";

import { useState, useCallback } from "react";
import { getBlogPosts, invalidateAnalyticsCache } from "@/lib/api";
import type { BlogPost } from "@/lib/types";

interface UseAnalyticsReturn {
  blogPosts: BlogPost[];
  isLoading: boolean;
  error: string | null;
  fetchPosts: (days?: number, limit?: number) => Promise<void>;
  refresh: () => Promise<void>;
}

export function useAnalytics(): UseAnalyticsReturn {
  const [blogPosts, setBlogPosts] = useState<BlogPost[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastDays, setLastDays] = useState(30);
  const [lastLimit, setLastLimit] = useState(20);

  const fetchPosts = useCallback(async (days = 30, limit = 20) => {
    setIsLoading(true);
    setError(null);
    setLastDays(days);
    setLastLimit(limit);

    try {
      const posts = await getBlogPosts(days, limit);
      setBlogPosts(posts);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to fetch blog posts";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      await invalidateAnalyticsCache();
      const posts = await getBlogPosts(lastDays, lastLimit);
      setBlogPosts(posts);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to refresh";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [lastDays, lastLimit]);

  return { blogPosts, isLoading, error, fetchPosts, refresh };
}
