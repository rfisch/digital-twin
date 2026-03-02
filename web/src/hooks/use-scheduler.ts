"use client";

import { useState, useCallback } from "react";
import {
  getScheduledPosts,
  schedulePost,
  cancelScheduledPost,
  reschedulePost,
} from "@/lib/api";
import type { ScheduledPost } from "@/lib/types";

interface UseSchedulerReturn {
  posts: ScheduledPost[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  schedule: (
    content: string,
    scheduledAt: string,
    sourceUrl?: string,
    feedbackId?: string,
  ) => Promise<string | null>;
  cancel: (id: string) => Promise<boolean>;
  reschedule: (id: string, newTime: string) => Promise<boolean>;
}

export function useScheduler(): UseSchedulerReturn {
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getScheduledPosts();
      setPosts(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to fetch scheduled posts";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const schedule = useCallback(
    async (
      content: string,
      scheduledAt: string,
      sourceUrl = "",
      feedbackId = "",
    ): Promise<string | null> => {
      setError(null);
      try {
        const result = await schedulePost({
          content,
          scheduled_at: scheduledAt,
          source_url: sourceUrl,
          feedback_id: feedbackId,
        });
        await refresh();
        return result.id;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to schedule post";
        setError(message);
        return null;
      }
    },
    [refresh],
  );

  const cancel = useCallback(
    async (id: string): Promise<boolean> => {
      setError(null);
      try {
        await cancelScheduledPost(id);
        await refresh();
        return true;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to cancel post";
        setError(message);
        return false;
      }
    },
    [refresh],
  );

  const rescheduleHandler = useCallback(
    async (id: string, newTime: string): Promise<boolean> => {
      setError(null);
      try {
        await reschedulePost(id, newTime);
        await refresh();
        return true;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to reschedule post";
        setError(message);
        return false;
      }
    },
    [refresh],
  );

  return {
    posts,
    isLoading,
    error,
    refresh,
    schedule,
    cancel,
    reschedule: rescheduleHandler,
  };
}
