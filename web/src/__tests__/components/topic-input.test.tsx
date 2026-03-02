import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TopicInput } from "@/components/topic-input";

describe("TopicInput", () => {
  it("renders for blog task", () => {
    render(<TopicInput value="" onChange={vi.fn()} taskType="blog" />);
    expect(screen.getByPlaceholderText(/blog post/i)).toBeInTheDocument();
  });

  it("hides for linkedin task", () => {
    const { container } = render(
      <TopicInput value="" onChange={vi.fn()} taskType="linkedin" />,
    );
    expect(container.innerHTML).toBe("");
  });

  it("hides for email_reply task", () => {
    const { container } = render(
      <TopicInput value="" onChange={vi.fn()} taskType="email_reply" />,
    );
    expect(container.innerHTML).toBe("");
  });

  it("updates placeholder per task type", () => {
    render(<TopicInput value="" onChange={vi.fn()} taskType="email" />);
    expect(screen.getByPlaceholderText(/email about/i)).toBeInTheDocument();
  });

  it("calls onChange on input", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TopicInput value="" onChange={onChange} taskType="blog" />);

    await user.type(screen.getByRole("textbox"), "hello");
    expect(onChange).toHaveBeenCalled();
  });
});
