import { describe, it, expect } from "vitest";
import { wordCount, charCount, formatDateTime, truncate } from "@/lib/utils";

describe("wordCount", () => {
  it("counts words in normal text", () => {
    expect(wordCount("hello world")).toBe(2);
  });

  it("returns 0 for empty string", () => {
    expect(wordCount("")).toBe(0);
  });

  it("returns 0 for whitespace only", () => {
    expect(wordCount("   ")).toBe(0);
  });

  it("handles multiple spaces between words", () => {
    expect(wordCount("hello   world")).toBe(2);
  });

  it("handles newlines and tabs", () => {
    expect(wordCount("hello\nworld\there")).toBe(3);
  });
});

describe("charCount", () => {
  it("counts characters including spaces", () => {
    expect(charCount("hello world")).toBe(11);
  });

  it("returns 0 for empty string", () => {
    expect(charCount("")).toBe(0);
  });
});

describe("formatDateTime", () => {
  it("formats a Unix timestamp", () => {
    const ts = 1709308800; // 2024-03-01 12:00:00 UTC
    const result = formatDateTime(ts);
    expect(result).toBeTruthy();
    expect(typeof result).toBe("string");
  });
});

describe("truncate", () => {
  it("returns full text if shorter than maxLength", () => {
    expect(truncate("hello", 10)).toBe("hello");
  });

  it("truncates with ellipsis if longer than maxLength", () => {
    expect(truncate("hello world foo bar", 10)).toBe("hello worl...");
  });

  it("returns full text if exactly maxLength", () => {
    expect(truncate("hello", 5)).toBe("hello");
  });
});
