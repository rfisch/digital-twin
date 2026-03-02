import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { GenerateButton } from "@/components/generate-button";

describe("GenerateButton", () => {
  it("renders Generate text", () => {
    render(<GenerateButton onClick={vi.fn()} isLoading={false} />);
    expect(screen.getByText("Generate")).toBeInTheDocument();
  });

  it("shows loading state", () => {
    render(<GenerateButton onClick={vi.fn()} isLoading={true} />);
    expect(screen.getByText("Generating...")).toBeInTheDocument();
  });

  it("is disabled when loading", () => {
    render(<GenerateButton onClick={vi.fn()} isLoading={true} />);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("is disabled when disabled prop is true", () => {
    render(<GenerateButton onClick={vi.fn()} isLoading={false} disabled />);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("calls onClick when clicked", async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<GenerateButton onClick={onClick} isLoading={false} />);

    await user.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledOnce();
  });
});
