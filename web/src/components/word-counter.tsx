"use client";

import { wordCount, charCount } from "@/lib/utils";
import { htmlToPlainText } from "./rich-editor";

interface WordCounterProps {
  text: string;
  charLimit?: number;
  isHtml?: boolean;
}

export function WordCounter({ text, charLimit = 3000, isHtml = false }: WordCounterProps) {
  const plainText = isHtml ? htmlToPlainText(text) : text;
  const words = wordCount(plainText);
  const chars = charCount(plainText);
  const isOverLimit = chars > charLimit;

  return (
    <p className="text-sm text-muted-foreground">
      {words} {words === 1 ? "word" : "words"} &middot;{" "}
      <span className={isOverLimit ? "text-destructive font-medium" : ""}>
        {chars.toLocaleString()} / {charLimit.toLocaleString()} chars
      </span>
    </p>
  );
}
