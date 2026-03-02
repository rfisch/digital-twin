import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { WordCounter } from "@/components/word-counter";

describe("WordCounter", () => {
  it("shows word and char counts", () => {
    render(<WordCounter text="hello world" />);
    expect(screen.getByText(/2 words/)).toBeInTheDocument();
    expect(screen.getByText(/11/)).toBeInTheDocument();
  });

  it("shows singular word for 1 word", () => {
    render(<WordCounter text="hello" />);
    expect(screen.getByText(/1 word\b/)).toBeInTheDocument();
  });

  it("shows 0 words for empty text", () => {
    render(<WordCounter text="" />);
    expect(screen.getByText(/0 words/)).toBeInTheDocument();
  });

  it("shows warning when over char limit", () => {
    const longText = "a".repeat(3001);
    render(<WordCounter text={longText} />);
    // The over-limit text should have destructive styling
    const charSpan = screen.getByText(/3,001/);
    expect(charSpan).toHaveClass("text-destructive");
  });

  it("uses default 3000 char limit", () => {
    render(<WordCounter text="hello" />);
    expect(screen.getByText(/3,000 chars/)).toBeInTheDocument();
  });
});
