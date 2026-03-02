import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ModelSettings } from "@/components/model-settings";

const defaultProps = {
  model: "jacq-v6:8b",
  onModelChange: vi.fn(),
  temperature: 0.7,
  onTemperatureChange: vi.fn(),
  maxTokens: 2048,
  onMaxTokensChange: vi.fn(),
  useRag: false,
  onUseRagChange: vi.fn(),
  availableModels: ["jacq-v6:8b", "llama3.1:8b"],
};

describe("ModelSettings", () => {
  it("renders accordion trigger", () => {
    render(<ModelSettings {...defaultProps} />);
    expect(screen.getByText("Model Settings")).toBeInTheDocument();
  });

  it("shows content when opened", async () => {
    const user = userEvent.setup();
    render(<ModelSettings {...defaultProps} />);

    await user.click(screen.getByText("Model Settings"));

    expect(screen.getByText("Temperature")).toBeInTheDocument();
    expect(screen.getByText("Max Tokens")).toBeInTheDocument();
    expect(screen.getByText("0.7")).toBeInTheDocument();
    expect(screen.getByText("2048")).toBeInTheDocument();
  });

  it("shows RAG checkbox", async () => {
    const user = userEvent.setup();
    render(<ModelSettings {...defaultProps} />);

    await user.click(screen.getByText("Model Settings"));

    expect(
      screen.getByText(/Use RAG/),
    ).toBeInTheDocument();
  });
});
