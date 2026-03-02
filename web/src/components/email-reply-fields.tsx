"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import type { EmailReplyFields as EmailReplyFieldsType } from "@/lib/types";

interface EmailReplyFieldsProps {
  fields: EmailReplyFieldsType;
  onChange: (fields: EmailReplyFieldsType) => void;
}

export function EmailReplyFields({ fields, onChange }: EmailReplyFieldsProps) {
  const update = (key: keyof EmailReplyFieldsType, value: string) => {
    onChange({ ...fields, [key]: value });
  };

  return (
    <Accordion type="single" collapsible defaultValue="email-reply-fields">
      <AccordionItem value="email-reply-fields">
        <AccordionTrigger className="text-sm font-medium">
          Email Reply Details
        </AccordionTrigger>
        <AccordionContent className="space-y-3 pt-2">
          <div className="space-y-1.5">
            <Label htmlFor="received-email">Received Email *</Label>
            <Textarea
              id="received-email"
              value={fields.receivedEmail}
              onChange={(e) => update("receivedEmail", e.target.value)}
              placeholder="Paste the email you're replying to..."
              rows={6}
              className="resize-y"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="sender-name">Sender Name</Label>
              <Input
                id="sender-name"
                value={fields.senderName}
                onChange={(e) => update("senderName", e.target.value)}
                placeholder="Jane Smith"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="sender-email">Sender Email</Label>
              <Input
                id="sender-email"
                value={fields.senderEmail}
                onChange={(e) => update("senderEmail", e.target.value)}
                placeholder="jane@example.com"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="reply-subject">Subject</Label>
            <Input
              id="reply-subject"
              value={fields.subject}
              onChange={(e) => update("subject", e.target.value)}
              placeholder="Re: ..."
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="reply-goal">Reply Goal</Label>
            <Input
              id="reply-goal"
              value={fields.goal}
              onChange={(e) => update("goal", e.target.value)}
              placeholder="What do you want to accomplish with this reply?"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="tone-notes">Tone Notes</Label>
            <Input
              id="tone-notes"
              value={fields.toneNotes}
              onChange={(e) => update("toneNotes", e.target.value)}
              placeholder="Any specific tone guidance?"
            />
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
