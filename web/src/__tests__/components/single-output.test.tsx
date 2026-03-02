import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { SingleOutput } from "@/components/single-output";

const mockResult = {
  text: "Generated text here",
  originalText: "Generated text here",
  promptInfo: null,
};

const defaultProps = {
  result: mockResult,
  taskType: "blog" as const,
  onTextChange: vi.fn(),
  onSave: vi.fn(),
  onSendEmail: vi.fn(),
  onPostLinkedIn: vi.fn(),
  gmailConfigured: true,
  linkedinConfigured: true,
  status: "",
};

describe("SingleOutput", () => {
  it("displays generated text", () => {
    render(<SingleOutput {...defaultProps} />);
    // Tiptap renders content in a contenteditable div, not a textarea
    expect(screen.getByText("Generated text here")).toBeInTheDocument();
  });

  it("shows Save Edits disabled when not edited", () => {
    render(<SingleOutput {...defaultProps} />);
    const saveBtn = screen.getByText("Save Edits").closest("button");
    expect(saveBtn).toBeDisabled();
  });

  it("enables Save Edits when text differs from original", () => {
    render(
      <SingleOutput
        {...defaultProps}
        result={{ ...mockResult, text: "Edited text" }}
      />,
    );
    const saveBtn = screen.getByText("Save Edits").closest("button");
    expect(saveBtn).not.toBeDisabled();
  });

  it("shows Send Email button for email task", () => {
    render(<SingleOutput {...defaultProps} taskType="email" />);
    expect(screen.getByText("Send Email")).toBeInTheDocument();
  });

  it("disables Send Email when gmail not configured", () => {
    render(
      <SingleOutput
        {...defaultProps}
        taskType="email"
        gmailConfigured={false}
      />,
    );
    const sendBtn = screen.getByText("Send Email").closest("button");
    expect(sendBtn).toBeDisabled();
  });

  it("disables Post to LinkedIn when not configured", () => {
    render(<SingleOutput {...defaultProps} linkedinConfigured={false} />);
    const postBtn = screen.getByText("Post to LinkedIn").closest("button");
    expect(postBtn).toBeDisabled();
  });

  it("shows status message", () => {
    render(<SingleOutput {...defaultProps} status="Edits saved" />);
    expect(screen.getByText("Edits saved")).toBeInTheDocument();
  });

  it("renders the rich editor for editing", () => {
    render(<SingleOutput {...defaultProps} />);
    // Tiptap creates a contenteditable div with ProseMirror class
    const editor = document.querySelector(".tiptap");
    expect(editor).toBeInTheDocument();
  });
});
