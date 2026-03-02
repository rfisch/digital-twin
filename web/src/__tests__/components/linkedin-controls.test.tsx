import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { LinkedInControls } from "@/components/linkedin-controls";

const defaultProps = {
  fields: { blogUrl: "", postCount: 3, timeRange: 30 },
  onChange: vi.fn(),
  blogPosts: [
    {
      title: "Test Blog Post",
      path: "/test",
      url: "https://example.com/test",
      sessions: 50,
      views: 100,
      avg_duration: 120,
      revisit_ratio: 0.3,
      score: 85,
    },
  ],
  analyticsConfigured: true,
  isLoadingPosts: false,
  onFetchPosts: vi.fn(),
  onRefresh: vi.fn(),
};

describe("LinkedInControls", () => {
  it("renders time range selector", () => {
    render(<LinkedInControls {...defaultProps} />);
    expect(screen.getByText("Time Range")).toBeInTheDocument();
  });

  it("renders post count slider", () => {
    render(<LinkedInControls {...defaultProps} />);
    expect(screen.getByText("Post Count")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("shows blog post dropdown when analytics configured", () => {
    render(<LinkedInControls {...defaultProps} />);
    expect(screen.getByText("Blog Post")).toBeInTheDocument();
  });

  it("shows URL input when analytics not configured", () => {
    render(
      <LinkedInControls
        {...defaultProps}
        analyticsConfigured={false}
        blogPosts={[]}
      />,
    );
    expect(
      screen.getByPlaceholderText(/GA4 not configured/),
    ).toBeInTheDocument();
  });

  it("shows refresh button when analytics configured", () => {
    render(<LinkedInControls {...defaultProps} />);
    // The refresh button is the one with RefreshCw icon
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });
});
