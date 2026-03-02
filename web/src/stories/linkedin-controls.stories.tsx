import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { LinkedInControls } from "@/components/linkedin-controls";

const meta: Meta<typeof LinkedInControls> = {
  title: "Components/LinkedInControls",
  component: LinkedInControls,
  args: {
    fields: { blogUrl: "", postCount: 3, timeRange: 30 },
    onChange: () => {},
    blogPosts: [],
    analyticsConfigured: true,
    isLoadingPosts: false,
    onFetchPosts: () => {},
    onRefresh: () => {},
  },
};
export default meta;

type Story = StoryObj<typeof LinkedInControls>;

export const WithBlogPosts: Story = {
  args: {
    blogPosts: [
      { title: "How To Design a Quarterly Plan", path: "/blog/quarterly-plan", url: "https://theintuitivewritingschool.com/blog/quarterly-plan", sessions: 150, views: 320, avg_duration: 180, revisit_ratio: 0.25, score: 92 },
      { title: "The Impossible Pursuit of Perfectionism", path: "/blog/perfectionism", url: "https://theintuitivewritingschool.com/blog/perfectionism", sessions: 98, views: 210, avg_duration: 145, revisit_ratio: 0.18, score: 85 },
      { title: "10 Practical Strategies for Email", path: "/blog/email-strategies", url: "https://theintuitivewritingschool.com/blog/email-strategies", sessions: 75, views: 160, avg_duration: 120, revisit_ratio: 0.22, score: 78 },
    ],
  },
};

export const EmptyState: Story = {
  args: { blogPosts: [], analyticsConfigured: true },
};

export const GA4NotConfigured: Story = {
  args: { analyticsConfigured: false, blogPosts: [] },
};

export const Loading: Story = {
  args: { isLoadingPosts: true },
};
