"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { EmailFields as EmailFieldsType } from "@/lib/types";

interface EmailFieldsProps {
  fields: EmailFieldsType;
  onChange: (fields: EmailFieldsType) => void;
}

const EMAIL_TYPES = [
  "Professional",
  "Personal",
  "Follow-up",
  "Introduction",
  "Thank you",
  "Request",
];

export function EmailFields({ fields, onChange }: EmailFieldsProps) {
  const update = (key: keyof EmailFieldsType, value: string) => {
    onChange({ ...fields, [key]: value });
  };

  return (
    <Accordion type="single" collapsible defaultValue="email-fields">
      <AccordionItem value="email-fields">
        <AccordionTrigger className="text-sm font-medium">
          Email Details
        </AccordionTrigger>
        <AccordionContent className="space-y-3 pt-2">
          <div className="space-y-1.5">
            <Label htmlFor="recipient">Recipient</Label>
            <Input
              id="recipient"
              value={fields.recipient}
              onChange={(e) => update("recipient", e.target.value)}
              placeholder="Who is this email for?"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="purpose">Purpose</Label>
            <Input
              id="purpose"
              value={fields.purpose}
              onChange={(e) => update("purpose", e.target.value)}
              placeholder="What's the purpose of this email?"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="email-type">Email Type</Label>
            <Select
              value={fields.emailType}
              onValueChange={(v) => update("emailType", v)}
            >
              <SelectTrigger id="email-type">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                {EMAIL_TYPES.map((type) => (
                  <SelectItem key={type} value={type.toLowerCase()}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
