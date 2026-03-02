import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { LinkedInOutput } from "@/components/linkedin-output";

const meta: Meta<typeof LinkedInOutput> = {
  title: "Components/LinkedInOutput",
  component: LinkedInOutput,
  args: {
    posts: [],
    onTextChange: () => {},
    onSave: () => {},
    onPostNow: () => {},
    onSchedule: () => {},
    onCancelPostSchedule: () => {},
    linkedinConfigured: true,
    postStatuses: {},
    postScheduledAts: {},
    scheduledPosts: [],
    onRefreshScheduled: () => {},
    onCancelScheduled: () => {},
    onRescheduleScheduled: () => {},
    isLoadingScheduled: false,
  },
};
export default meta;

type Story = StoryObj<typeof LinkedInOutput>;

const samplePost = (n: number) => ({
  text: `Post ${n}: I've been thinking about what it means to show up as a writer — not the polished version, but the messy one. The truth is, most of the best writing starts with not knowing what you're doing.`,
  originalText: `Post ${n}: I've been thinking about what it means to show up as a writer — not the polished version, but the messy one. The truth is, most of the best writing starts with not knowing what you're doing.`,
  promptInfo: null,
});

export const OnePost: Story = {
  args: { posts: [samplePost(1)] },
};

export const ThreePosts: Story = {
  args: {
    posts: [samplePost(1), samplePost(2), samplePost(3)],
  },
};

export const FivePosts: Story = {
  args: {
    posts: [samplePost(1), samplePost(2), samplePost(3), samplePost(4), samplePost(5)],
  },
};

export const MixedStatuses: Story = {
  args: {
    posts: [samplePost(1), samplePost(2), samplePost(3)],
    postStatuses: { 0: "Posted to LinkedIn", 2: "Scheduled (abc12345)" },
    postScheduledAts: { 2: new Date(Date.now() + 86400000).toISOString() },
  },
};

export const WithScheduledPosts: Story = {
  args: {
    posts: [samplePost(1)],
    scheduledPosts: [
      { id: "abc-123", content: "Scheduled post content here...", scheduled_at: new Date(Date.now() + 86400000).toISOString(), created_at: new Date().toISOString(), status: "pending" },
      { id: "def-456", content: "Another scheduled post...", scheduled_at: new Date(Date.now() + 172800000).toISOString(), created_at: new Date().toISOString(), status: "pending" },
    ],
  },
};
