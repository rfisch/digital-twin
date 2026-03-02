import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { LinkedInPostCard } from "@/components/linkedin-post-card";

const defaultProps = {
  index: 0,
  post: {
    text: "Test post content",
    originalText: "Test post content",
    promptInfo: null,
  },
  onTextChange: vi.fn(),
  onSave: vi.fn(),
  onPostNow: vi.fn(),
  onSchedule: vi.fn(),
  linkedinConfigured: true,
  status: "",
};

describe("LinkedInPostCard", () => {
  it("shows editable content", () => {
    render(<LinkedInPostCard {...defaultProps} />);
    // Tiptap renders content in a contenteditable div, not a textarea
    expect(screen.getByText("Test post content")).toBeInTheDocument();
  });

  it("shows word count", () => {
    render(<LinkedInPostCard {...defaultProps} />);
    expect(screen.getByText(/3 words/)).toBeInTheDocument();
  });

  it("shows Save, Post Now, Schedule buttons", () => {
    render(<LinkedInPostCard {...defaultProps} />);
    expect(screen.getByText("Save Edits")).toBeInTheDocument();
    expect(screen.getByText("Post Now")).toBeInTheDocument();
    expect(screen.getByText("Schedule")).toBeInTheDocument();
  });

  it("Save Edits disabled when not edited", () => {
    render(<LinkedInPostCard {...defaultProps} />);
    const saveBtn = screen.getByText("Save Edits").closest("button");
    expect(saveBtn).toBeDisabled();
  });

  it("Post Now disabled when linkedin not configured", () => {
    render(<LinkedInPostCard {...defaultProps} linkedinConfigured={false} />);
    const postBtn = screen.getByText("Post Now").closest("button");
    expect(postBtn).toBeDisabled();
  });

  it("renders the rich editor", () => {
    render(<LinkedInPostCard {...defaultProps} />);
    const editor = document.querySelector(".tiptap");
    expect(editor).toBeInTheDocument();
  });

  it("shows status message", () => {
    render(<LinkedInPostCard {...defaultProps} status="Posted to LinkedIn" />);
    expect(screen.getByText("Posted to LinkedIn")).toBeInTheDocument();
  });
});
