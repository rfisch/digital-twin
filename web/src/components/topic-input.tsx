"use client";

import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import type { TaskType } from "@/lib/types";

interface TopicInputProps {
  value: string;
  onChange: (value: string) => void;
  taskType: TaskType;
}

const PLACEHOLDERS: Partial<Record<TaskType, string>> = {
  blog: "What should the blog post be about?",
  email: "What's the email about?",
  copywriting: "What are you writing copy for?",
  freeform: "What would you like to write about?",
};

const LABELS: Partial<Record<TaskType, string>> = {
  blog: "Topic",
  email: "Topic",
  copywriting: "Topic",
  freeform: "Topic",
};

export function TopicInput({ value, onChange, taskType }: TopicInputProps) {
  // Hidden for LinkedIn and Email Reply
  if (taskType === "linkedin" || taskType === "email_reply") {
    return null;
  }

  return (
    <div className="space-y-2">
      <Label htmlFor="topic">{LABELS[taskType] || "Topic"}</Label>
      <Textarea
        id="topic"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={PLACEHOLDERS[taskType] || "Enter your topic..."}
        rows={4}
        className="resize-y"
      />
    </div>
  );
}
