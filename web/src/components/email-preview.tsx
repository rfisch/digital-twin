"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface EmailPreviewProps {
  html: string;
}

export function EmailPreview({ html }: EmailPreviewProps) {
  if (!html) return null;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Email Preview</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className="prose prose-sm max-w-none dark:prose-invert"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      </CardContent>
    </Card>
  );
}
