import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { LinkedInOutput } from "@/components/linkedin-output";

const mockPosts = [
  { text: "Post 1 content", originalText: "Post 1 content", promptInfo: null },
  { text: "Post 2 content", originalText: "Post 2 content", promptInfo: null },
  { text: "Post 3 content", originalText: "Post 3 content", promptInfo: null },
];

const defaultProps = {
  posts: mockPosts,
  onTextChange: vi.fn(),
  onSave: vi.fn(),
  onPostNow: vi.fn(),
  onSchedule: vi.fn(),
  onCancelPostSchedule: vi.fn(),
  linkedinConfigured: true,
  postStatuses: {},
  postScheduledAts: {},
  scheduledPosts: [],
  onRefreshScheduled: vi.fn(),
  onCancelScheduled: vi.fn(),
  onRescheduleScheduled: vi.fn(),
  isLoadingScheduled: false,
};

describe("LinkedInOutput", () => {
  it("renders N accordion items", () => {
    render(<LinkedInOutput {...defaultProps} />);
    expect(screen.getByText("Post 1")).toBeInTheDocument();
    expect(screen.getByText("Post 2")).toBeInTheDocument();
    expect(screen.getByText("Post 3")).toBeInTheDocument();
  });

  it("all posts are visible in DOM simultaneously (Gradio bug fix)", () => {
    render(<LinkedInOutput {...defaultProps} />);
    // Tiptap renders content in contenteditable divs, not textareas
    expect(screen.getByText("Post 1 content")).toBeInTheDocument();
    expect(screen.getByText("Post 2 content")).toBeInTheDocument();
    expect(screen.getByText("Post 3 content")).toBeInTheDocument();
  });

  it("renders 1 post", () => {
    render(
      <LinkedInOutput
        {...defaultProps}
        posts={[mockPosts[0]]}
      />,
    );
    expect(screen.getByText("Post 1")).toBeInTheDocument();
    expect(screen.getByText("Post 1 content")).toBeInTheDocument();
  });

  it("renders 5 posts", () => {
    const fivePosts = Array.from({ length: 5 }, (_, i) => ({
      text: `Post ${i + 1} text`,
      originalText: `Post ${i + 1} text`,
      promptInfo: null,
    }));
    render(<LinkedInOutput {...defaultProps} posts={fivePosts} />);
    for (let i = 1; i <= 5; i++) {
      expect(screen.getByText(`Post ${i}`)).toBeInTheDocument();
    }
  });

  it("shows scheduled posts section", () => {
    render(<LinkedInOutput {...defaultProps} />);
    expect(screen.getByText(/Scheduled Posts/)).toBeInTheDocument();
  });
});
