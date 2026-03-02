"use client";

import { useState } from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { SchedulePicker } from "./schedule-picker";
import { RefreshCw, X, CalendarClock } from "lucide-react";
import { formatDateTime, truncate } from "@/lib/utils";
import type { ScheduledPost } from "@/lib/types";

interface ScheduledPostsTableProps {
  posts: ScheduledPost[];
  onRefresh: () => void;
  onCancel: (id: string) => void;
  onReschedule: (id: string, newTime: string) => void;
  isLoading: boolean;
}

export function ScheduledPostsTable({
  posts,
  onRefresh,
  onCancel,
  onReschedule,
  isLoading,
}: ScheduledPostsTableProps) {
  const [reschedulingId, setReschedulingId] = useState<string | null>(null);
  const [rescheduleDate, setRescheduleDate] = useState<Date | null>(null);

  const handleReschedule = (id: string) => {
    if (rescheduleDate) {
      onReschedule(id, rescheduleDate.toISOString());
      setReschedulingId(null);
      setRescheduleDate(null);
    }
  };

  return (
    <Accordion type="single" collapsible>
      <AccordionItem value="scheduled-posts">
        <AccordionTrigger className="text-sm font-medium">
          Scheduled Posts ({posts.length})
        </AccordionTrigger>
        <AccordionContent>
          <div className="flex justify-end mb-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={onRefresh}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            </Button>
          </div>

          {posts.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              No scheduled posts
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-24">ID</TableHead>
                  <TableHead>Scheduled For</TableHead>
                  <TableHead>Preview</TableHead>
                  <TableHead className="w-32">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {posts.map((post) => (
                  <TableRow key={post.id}>
                    <TableCell className="font-mono text-xs">
                      {post.id.slice(0, 8)}
                    </TableCell>
                    <TableCell className="text-sm">
                      {formatDateTime(post.scheduled_at)}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {truncate(post.content, 60)}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onCancel(post.id)}
                          title="Cancel"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setReschedulingId(
                              reschedulingId === post.id ? null : post.id,
                            );
                            setRescheduleDate(null);
                          }}
                          title="Reschedule"
                        >
                          <CalendarClock className="h-4 w-4" />
                        </Button>
                      </div>
                      {reschedulingId === post.id && (
                        <div className="mt-2 flex gap-2 items-center">
                          <SchedulePicker
                            value={rescheduleDate}
                            onChange={setRescheduleDate}
                          />
                          <Button
                            size="sm"
                            onClick={() => handleReschedule(post.id)}
                            disabled={!rescheduleDate}
                          >
                            Save
                          </Button>
                        </div>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
