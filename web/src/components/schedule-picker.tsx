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
import { CalendarIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface SchedulePickerProps {
  value: Date | null;
  onChange: (date: Date | null) => void;
}

export function SchedulePicker({ value, onChange }: SchedulePickerProps) {
  const [isOpen, setIsOpen] = useState(false);

  const hours = Array.from({ length: 24 }, (_, i) => i);
  const minutes = Array.from({ length: 12 }, (_, i) => i * 5);

  const currentHour = value ? value.getHours() : 9;
  const currentMinute = value ? value.getMinutes() : 0;

  const handleDateSelect = (date: Date | undefined) => {
    if (!date) {
      onChange(null);
      return;
    }
    const newDate = new Date(date);
    newDate.setHours(currentHour, currentMinute, 0, 0);
    onChange(newDate);
  };

  const handleTimeChange = (type: "hour" | "minute", val: string) => {
    const base = value || new Date();
    const newDate = new Date(base);
    if (type === "hour") {
      newDate.setHours(Number(val));
    } else {
      newDate.setMinutes(Number(val));
    }
    onChange(newDate);
  };

  const formatDisplay = (date: Date | null) => {
    if (!date) return "Pick date & time";
    return date.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={cn(
            "justify-start text-left font-normal",
            !value && "text-muted-foreground",
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {formatDisplay(value)}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar
          mode="single"
          selected={value || undefined}
          onSelect={handleDateSelect}
          disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
        />
        <div className="flex gap-2 border-t p-3">
          <Select
            value={String(currentHour)}
            onValueChange={(v) => handleTimeChange("hour", v)}
          >
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
          <span className="flex items-center">:</span>
          <Select
            value={String(currentMinute)}
            onValueChange={(v) => handleTimeChange("minute", v)}
          >
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
      </PopoverContent>
    </Popover>
  );
}
