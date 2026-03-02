import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TaskSelector } from "@/components/task-selector";

describe("TaskSelector", () => {
  it("renders with current value", () => {
    render(<TaskSelector value="blog" onChange={vi.fn()} />);
    expect(screen.getByText("Blog Post")).toBeInTheDocument();
  });

  it("shows all task types when opened", async () => {
    const user = userEvent.setup();
    render(<TaskSelector value="blog" onChange={vi.fn()} />);

    await user.click(screen.getByRole("combobox"));

    // "Blog Post" appears both as selected value and dropdown option
    expect(screen.getAllByText("Blog Post").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("Email Reply")).toBeInTheDocument();
    expect(screen.getByText("Copywriting")).toBeInTheDocument();
    expect(screen.getByText("LinkedIn Post")).toBeInTheDocument();
    expect(screen.getByText("Freeform")).toBeInTheDocument();
  });

  it("calls onChange when selection changes", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TaskSelector value="blog" onChange={onChange} />);

    await user.click(screen.getByRole("combobox"));
    await user.click(screen.getByText("Email"));

    expect(onChange).toHaveBeenCalledWith("email");
  });
});
