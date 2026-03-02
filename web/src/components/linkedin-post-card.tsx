"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { WordCounter } from "./word-counter";
import { RichEditor, htmlToPlainText } from "./rich-editor";
import { Save, Send, CalendarClock, X } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PostResult } from "@/lib/types";

interface LinkedInPostCardProps {
  index: number;
  post: PostResult;
  onTextChange: (text: string) => void;
  onSave: () => void;
  onPostNow: () => void;
  onSchedule: (scheduledAt: string) => void;
  onCancelSchedule?: () => void;
  linkedinConfigured: boolean;
  scheduledAt?: string | null;
  status?: string;
}

export function LinkedInPostCard({
  index,
  post,
  onTextChange,
  onSave,
  onPostNow,
  onSchedule,
  onCancelSchedule,
  linkedinConfigured,
  scheduledAt,
  status,
}: LinkedInPostCardProps) {
  const [isScheduleOpen, setIsScheduleOpen] = useState(false);
  const [pickedDate, setPickedDate] = useState<Date | undefined>(undefined);
  const [pickedHour, setPickedHour] = useState("9");
  const [pickedMinute, setPickedMinute] = useState("0");

  // Compare as plain text so HTML conversion doesn't trigger false edits
  const isEdited = htmlToPlainText(post.text) !== htmlToPlainText(post.originalText);

  const hours = Array.from({ length: 24 }, (_, i) => i);
  const minutes = Array.from({ length: 12 }, (_, i) => i * 5);

  const handleConfirmSchedule = () => {
    if (!pickedDate) return;
    const dt = new Date(pickedDate);
    dt.setHours(Number(pickedHour), Number(pickedMinute), 0, 0);
    onSchedule(dt.toISOString());
    setIsScheduleOpen(false);
  };

  const formatScheduled = (iso: string) => {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  return (
    <div className="space-y-3">
      <RichEditor
        content={post.text}
        onChange={onTextChange}
        placeholder={`Post ${index + 1} content...`}
        minHeight="200px"
      />

      <WordCounter text={post.text} isHtml />

      <div className="flex flex-wrap items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onSave}
          disabled={!isEdited}
        >
          <Save className="mr-2 h-4 w-4" />
          Save Edits
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={onPostNow}
          disabled={!linkedinConfigured || !post.text}
        >
          <Send className="mr-2 h-4 w-4" />
          Post Now
        </Button>

        {/* Schedule — single button opens popover */}
        {scheduledAt ? (
          <div className="flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm">
            <CalendarClock className="h-4 w-4 text-muted-foreground" />
            <span>{formatScheduled(scheduledAt)}</span>
            <Popover open={isScheduleOpen} onOpenChange={setIsScheduleOpen}>
              <PopoverTrigger asChild>
                <Button variant="ghost" size="sm" className="h-6 px-1.5 ml-1">
                  Reschedule
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={pickedDate}
                  onSelect={setPickedDate}
                  disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
                />
                <div className="flex items-center gap-2 border-t p-3">
                  <Select value={pickedHour} onValueChange={setPickedHour}>
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {hours.map((h) => (
                        <SelectItem key={h} value={String(h)}>
                          {String(h).padStart(2, "0")}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <span>:</span>
                  <Select value={pickedMinute} onValueChange={setPickedMinute}>
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {minutes.map((m) => (
                        <SelectItem key={m} value={String(m)}>
                          {String(m).padStart(2, "0")}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex justify-end gap-2 border-t p-3">
                  <Button variant="ghost" size="sm" onClick={() => setIsScheduleOpen(false)}>
                    Cancel
                  </Button>
                  <Button size="sm" onClick={handleConfirmSchedule} disabled={!pickedDate}>
                    Update
                  </Button>
                </div>
              </PopoverContent>
            </Popover>
            {onCancelSchedule && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 ml-0.5"
                onClick={onCancelSchedule}
                title="Cancel schedule"
              >
                <X className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>
        ) : (
          <Popover open={isScheduleOpen} onOpenChange={setIsScheduleOpen}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                disabled={!post.text}
              >
                <CalendarClock className="mr-2 h-4 w-4" />
                Schedule
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={pickedDate}
                onSelect={setPickedDate}
                disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
              />
              <div className="flex items-center gap-2 border-t p-3">
                <Select value={pickedHour} onValueChange={setPickedHour}>
                  <SelectTrigger className="w-20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {hours.map((h) => (
                      <SelectItem key={h} value={String(h)}>
                        {String(h).padStart(2, "0")}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <span>:</span>
                <Select value={pickedMinute} onValueChange={setPickedMinute}>
                  <SelectTrigger className="w-20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {minutes.map((m) => (
                      <SelectItem key={m} value={String(m)}>
                        {String(m).padStart(2, "0")}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex justify-end gap-2 border-t p-3">
                <Button variant="ghost" size="sm" onClick={() => setIsScheduleOpen(false)}>
                  Cancel
                </Button>
                <Button size="sm" onClick={handleConfirmSchedule} disabled={!pickedDate}>
                  Confirm
                </Button>
              </div>
            </PopoverContent>
          </Popover>
        )}
      </div>

      {status && (
        <p className={cn(
          "text-sm",
          status.startsWith("Error") ? "text-destructive" : "text-muted-foreground",
        )}>{status}</p>
      )}
    </div>
  );
}
