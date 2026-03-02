import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SchedulePicker } from "@/components/schedule-picker";

describe("SchedulePicker", () => {
  it("renders with placeholder text when no value", () => {
    render(<SchedulePicker value={null} onChange={vi.fn()} />);
    expect(screen.getByText("Pick date & time")).toBeInTheDocument();
  });

  it("displays formatted date when value is set", () => {
    const date = new Date(2026, 2, 15, 14, 30); // Mar 15, 2026 2:30 PM
    render(<SchedulePicker value={date} onChange={vi.fn()} />);
    // Should show something like "Mar 15, 2026, 2:30 PM"
    const button = screen.getByRole("button");
    expect(button.textContent).toContain("Mar");
    expect(button.textContent).toContain("15");
  });

  it("opens calendar popover on click", async () => {
    const user = userEvent.setup();
    render(<SchedulePicker value={null} onChange={vi.fn()} />);

    await user.click(screen.getByRole("button"));

    // Calendar should be visible (it renders day buttons)
    const gridcells = screen.getAllByRole("gridcell");
    expect(gridcells.length).toBeGreaterThan(0);
  });
});
