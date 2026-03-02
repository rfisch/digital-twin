"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { LinkedInPostCard } from "./linkedin-post-card";
import { ScheduledPostsTable } from "./scheduled-posts-table";
import type { PostResult, ScheduledPost } from "@/lib/types";

interface LinkedInOutputProps {
  posts: PostResult[];
  onTextChange: (index: number, text: string) => void;
  onSave: (index: number) => void;
  onPostNow: (index: number) => void;
  onSchedule: (index: number, scheduledAt: string) => void;
  onCancelPostSchedule: (index: number) => void;
  linkedinConfigured: boolean;
  postStatuses: Record<number, string>;
  postScheduledAts: Record<number, string | null>;
  // Scheduled posts
  scheduledPosts: ScheduledPost[];
  onRefreshScheduled: () => void;
  onCancelScheduled: (id: string) => void;
  onRescheduleScheduled: (id: string, newTime: string) => void;
  isLoadingScheduled: boolean;
}

export function LinkedInOutput({
  posts,
  onTextChange,
  onSave,
  onPostNow,
  onSchedule,
  onCancelPostSchedule,
  linkedinConfigured,
  postStatuses,
  postScheduledAts,
  scheduledPosts,
  onRefreshScheduled,
  onCancelScheduled,
  onRescheduleScheduled,
  isLoadingScheduled,
}: LinkedInOutputProps) {
  // All items open by default
  const defaultOpen = posts.map((_, i) => `post-${i}`);

  return (
    <div className="space-y-6">
      {posts.length > 0 && (
        <Accordion type="multiple" defaultValue={defaultOpen}>
          {posts.map((post, i) => (
            <AccordionItem key={i} value={`post-${i}`}>
              <AccordionTrigger className="text-sm font-medium">
                Post {i + 1}
              </AccordionTrigger>
              <AccordionContent>
                <LinkedInPostCard
                  index={i}
                  post={post}
                  onTextChange={(text) => onTextChange(i, text)}
                  onSave={() => onSave(i)}
                  onPostNow={() => onPostNow(i)}
                  onSchedule={(scheduledAt) => onSchedule(i, scheduledAt)}
                  onCancelSchedule={() => onCancelPostSchedule(i)}
                  linkedinConfigured={linkedinConfigured}
                  scheduledAt={postScheduledAts[i]}
                  status={postStatuses[i]}
                />
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      )}

      <ScheduledPostsTable
        posts={scheduledPosts}
        onRefresh={onRefreshScheduled}
        onCancel={onCancelScheduled}
        onReschedule={onRescheduleScheduled}
        isLoading={isLoadingScheduled}
      />
    </div>
  );
}
