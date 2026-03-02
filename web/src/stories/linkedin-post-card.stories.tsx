import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { LinkedInPostCard } from "@/components/linkedin-post-card";

const meta: Meta<typeof LinkedInPostCard> = {
  title: "Components/LinkedInPostCard",
  component: LinkedInPostCard,
  args: {
    index: 0,
    post: {
      text: "I've been thinking a lot about what it means to show up as a writer — not the polished, Instagram-ready version, but the messy, uncertain, still-figuring-it-out version.\n\nThe truth is, most of the best writing I've ever done started with me not knowing what the hell I was doing.",
      originalText: "I've been thinking a lot about what it means to show up as a writer — not the polished, Instagram-ready version, but the messy, uncertain, still-figuring-it-out version.\n\nThe truth is, most of the best writing I've ever done started with me not knowing what the hell I was doing.",
      promptInfo: null,
    },
    onTextChange: () => {},
    onSave: () => {},
    onPostNow: () => {},
    onSchedule: () => {},
    linkedinConfigured: true,
    status: "",
  },
};
export default meta;

type Story = StoryObj<typeof LinkedInPostCard>;

export const Default: Story = {};

export const Empty: Story = {
  args: {
    post: { text: "", originalText: "", promptInfo: null },
  },
};

export const WithSchedule: Story = {
  args: {
    scheduledAt: new Date(Date.now() + 86400000).toISOString(),
    onCancelSchedule: () => {},
  },
};

export const Posted: Story = {
  args: { status: "Posted to LinkedIn" },
};

export const LinkedInNotConfigured: Story = {
  args: { linkedinConfigured: false },
};

export const Edited: Story = {
  args: {
    post: {
      text: "Edited version of the post with changes made by Jacq.",
      originalText: "Original generated version of the post.",
      promptInfo: null,
    },
  },
};
