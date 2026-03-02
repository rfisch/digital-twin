"use client";

import { SingleOutput } from "./single-output";
import { LinkedInOutput } from "./linkedin-output";
import type { TaskType, PostResult, ScheduledPost } from "@/lib/types";

interface OutputPanelProps {
  taskType: TaskType;
  // Single output
  singleOutput: PostResult | null;
  onSingleTextChange: (text: string) => void;
  onSingleSave: () => void;
  onSendEmail?: () => void;
  onPostLinkedIn?: () => void;
  gmailConfigured: boolean;
  linkedinConfigured: boolean;
  singleStatus?: string;
  // LinkedIn output
  linkedinPosts: PostResult[];
  onLinkedInTextChange: (index: number, text: string) => void;
  onLinkedInSave: (index: number) => void;
  onLinkedInPostNow: (index: number) => void;
  onLinkedInSchedule: (index: number, scheduledAt: string) => void;
  onLinkedInCancelSchedule: (index: number) => void;
  linkedinPostStatuses: Record<number, string>;
  linkedinPostScheduledAts: Record<number, string | null>;
  // Scheduled posts
  scheduledPosts: ScheduledPost[];
  onRefreshScheduled: () => void;
  onCancelScheduled: (id: string) => void;
  onRescheduleScheduled: (id: string, newTime: string) => void;
  isLoadingScheduled: boolean;
}

export function OutputPanel({
  taskType,
  singleOutput,
  onSingleTextChange,
  onSingleSave,
  onSendEmail,
  onPostLinkedIn,
  gmailConfigured,
  linkedinConfigured,
  singleStatus,
  linkedinPosts,
  onLinkedInTextChange,
  onLinkedInSave,
  onLinkedInPostNow,
  onLinkedInSchedule,
  onLinkedInCancelSchedule,
  linkedinPostStatuses,
  linkedinPostScheduledAts,
  scheduledPosts,
  onRefreshScheduled,
  onCancelScheduled,
  onRescheduleScheduled,
  isLoadingScheduled,
}: OutputPanelProps) {
  if (taskType === "linkedin") {
    if (linkedinPosts.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          Select a blog post and generate LinkedIn posts
        </div>
      );
    }

    return (
      <LinkedInOutput
        posts={linkedinPosts}
        onTextChange={onLinkedInTextChange}
        onSave={onLinkedInSave}
        onPostNow={onLinkedInPostNow}
        onSchedule={onLinkedInSchedule}
        onCancelPostSchedule={onLinkedInCancelSchedule}
        linkedinConfigured={linkedinConfigured}
        postStatuses={linkedinPostStatuses}
        postScheduledAts={linkedinPostScheduledAts}
        scheduledPosts={scheduledPosts}
        onRefreshScheduled={onRefreshScheduled}
        onCancelScheduled={onCancelScheduled}
        onRescheduleScheduled={onRescheduleScheduled}
        isLoadingScheduled={isLoadingScheduled}
      />
    );
  }

  if (!singleOutput) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        Enter a topic and click Generate
      </div>
    );
  }

  return (
    <SingleOutput
      result={singleOutput}
      taskType={taskType}
      onTextChange={onSingleTextChange}
      onSave={onSingleSave}
      onSendEmail={onSendEmail}
      onPostLinkedIn={onPostLinkedIn}
      gmailConfigured={gmailConfigured}
      linkedinConfigured={linkedinConfigured}
      status={singleStatus}
    />
  );
}
