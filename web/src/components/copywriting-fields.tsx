"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { CopywritingFields as CopywritingFieldsType } from "@/lib/types";

interface CopywritingFieldsProps {
  fields: CopywritingFieldsType;
  onChange: (fields: CopywritingFieldsType) => void;
}

export function CopywritingFields({ fields, onChange }: CopywritingFieldsProps) {
  const update = (key: keyof CopywritingFieldsType, value: string) => {
    onChange({ ...fields, [key]: value });
  };

  return (
    <Accordion type="single" collapsible defaultValue="copywriting-fields">
      <AccordionItem value="copywriting-fields">
        <AccordionTrigger className="text-sm font-medium">
          Copywriting Details
        </AccordionTrigger>
        <AccordionContent className="space-y-3 pt-2">
          <div className="space-y-1.5">
            <Label htmlFor="medium">Medium</Label>
            <Input
              id="medium"
              value={fields.medium}
              onChange={(e) => update("medium", e.target.value)}
              placeholder="e.g., landing page, ad copy, social media"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="audience">Audience</Label>
            <Input
              id="audience"
              value={fields.audience}
              onChange={(e) => update("audience", e.target.value)}
              placeholder="Who is this for?"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="copy-message">Key Message</Label>
            <Input
              id="copy-message"
              value={fields.message}
              onChange={(e) => update("message", e.target.value)}
              placeholder="What's the main message?"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="copy-tone">Tone</Label>
            <Input
              id="copy-tone"
              value={fields.tone}
              onChange={(e) => update("tone", e.target.value)}
              placeholder="e.g., professional, casual, urgent"
            />
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
