"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { TASK_LABELS, type TaskType } from "@/lib/types";

interface TaskSelectorProps {
  value: TaskType;
  onChange: (value: TaskType) => void;
}

export function TaskSelector({ value, onChange }: TaskSelectorProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="task-type">Task Type</Label>
      <Select value={value} onValueChange={(v) => onChange(v as TaskType)}>
        <SelectTrigger id="task-type" className="w-full">
          <SelectValue placeholder="Select task type" />
        </SelectTrigger>
        <SelectContent>
          {(Object.entries(TASK_LABELS) as [TaskType, string][]).map(([key, label]) => (
            <SelectItem key={key} value={key}>
              {label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
