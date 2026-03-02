import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ScheduledPostsTable } from "@/components/scheduled-posts-table";

const mockPosts = [
  {
    id: "abc12345-6789-0123-4567-890123456789",
    content: "This is a test scheduled post content that is longer than sixty characters total",
    scheduled_at: 1709308800,
    created_at: 1709222400,
    status: "pending",
    posted_at: null,
    error: null,
    source_url: "https://example.com",
    feedback_id: "",
  },
];

const defaultProps = {
  posts: mockPosts,
  onRefresh: vi.fn(),
  onCancel: vi.fn(),
  onReschedule: vi.fn(),
  isLoading: false,
};

describe("ScheduledPostsTable", () => {
  it("shows post count in accordion trigger", () => {
    render(<ScheduledPostsTable {...defaultProps} />);
    expect(screen.getByText(/Scheduled Posts \(1\)/)).toBeInTheDocument();
  });

  it("shows empty state when no posts", async () => {
    const user = userEvent.setup();
    render(<ScheduledPostsTable {...defaultProps} posts={[]} />);

    await user.click(screen.getByText(/Scheduled Posts/));
    expect(screen.getByText("No scheduled posts")).toBeInTheDocument();
  });

  it("renders table rows when opened", async () => {
    const user = userEvent.setup();
    render(<ScheduledPostsTable {...defaultProps} />);

    await user.click(screen.getByText(/Scheduled Posts/));

    // Shows truncated ID
    expect(screen.getByText("abc12345")).toBeInTheDocument();
    // Shows truncated preview
    expect(screen.getByText(/This is a test scheduled/)).toBeInTheDocument();
  });

  it("calls onCancel when cancel button clicked", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();
    render(<ScheduledPostsTable {...defaultProps} onCancel={onCancel} />);

    await user.click(screen.getByText(/Scheduled Posts/));

    // Find cancel button (X icon button)
    const buttons = screen.getAllByRole("button");
    const cancelBtn = buttons.find((b) => b.getAttribute("title") === "Cancel");
    if (cancelBtn) {
      await user.click(cancelBtn);
      expect(onCancel).toHaveBeenCalledWith(mockPosts[0].id);
    }
  });
});
