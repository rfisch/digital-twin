"use client";

import { Button } from "@/components/ui/button";
import { WordCounter } from "./word-counter";
import { EmailPreview } from "./email-preview";
import { RichEditor, htmlToPlainText } from "./rich-editor";
import { Save, Send, Linkedin } from "lucide-react";
import type { PostResult, TaskType } from "@/lib/types";

interface SingleOutputProps {
  result: PostResult;
  taskType: TaskType;
  onTextChange: (text: string) => void;
  onSave: () => void;
  onSendEmail?: () => void;
  onPostLinkedIn?: () => void;
  gmailConfigured: boolean;
  linkedinConfigured: boolean;
  status?: string;
}

export function SingleOutput({
  result,
  taskType,
  onTextChange,
  onSave,
  onSendEmail,
  onPostLinkedIn,
  gmailConfigured,
  linkedinConfigured,
  status,
}: SingleOutputProps) {
  // Compare as plain text so format conversion doesn't trigger false edits
  const isEdited = htmlToPlainText(result.text) !== htmlToPlainText(result.originalText);

  return (
    <div className="space-y-4">
      {taskType === "email_reply" && result.text && (
        <EmailPreview html={result.text} />
      )}

      <RichEditor
        content={result.text}
        onChange={onTextChange}
        placeholder="Generated text will appear here..."
        minHeight="400px"
      />

      <WordCounter text={result.text} isHtml />

      <div className="flex gap-2 flex-wrap">
        <Button
          variant="outline"
          size="sm"
          onClick={onSave}
          disabled={!isEdited}
        >
          <Save className="mr-2 h-4 w-4" />
          Save Edits
        </Button>

        {(taskType === "email" || taskType === "email_reply") && (
          <Button
            variant="outline"
            size="sm"
            onClick={onSendEmail}
            disabled={!gmailConfigured || !result.text}
          >
            <Send className="mr-2 h-4 w-4" />
            Send Email
          </Button>
        )}

        <Button
          variant="outline"
          size="sm"
          onClick={onPostLinkedIn}
          disabled={!linkedinConfigured || !result.text}
        >
          <Linkedin className="mr-2 h-4 w-4" />
          Post to LinkedIn
        </Button>
      </div>

      {status && (
        <p className="text-sm text-muted-foreground">{status}</p>
      )}
    </div>
  );
}
