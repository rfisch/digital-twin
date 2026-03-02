import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { ScheduledPostsTable } from "@/components/scheduled-posts-table";

const meta: Meta<typeof ScheduledPostsTable> = {
  title: "Components/ScheduledPostsTable",
  component: ScheduledPostsTable,
  args: {
    posts: [],
    onRefresh: () => {},
    onCancel: () => {},
    onReschedule: () => {},
    isLoading: false,
  },
};
export default meta;

type Story = StoryObj<typeof ScheduledPostsTable>;

export const WithPosts: Story = {
  args: {
    posts: [
      { id: "abc-12345678", content: "I've been thinking about what it means to show up as a writer — the messy version.", scheduled_at: new Date(Date.now() + 86400000).toISOString(), created_at: new Date().toISOString(), status: "pending" },
      { id: "def-87654321", content: "Your writing doesn't need permission to exist. Just write the damn thing.", scheduled_at: new Date(Date.now() + 172800000).toISOString(), created_at: new Date().toISOString(), status: "pending" },
      { id: "ghi-11223344", content: "What if the block isn't about writing at all? What if it's about fear of being seen?", scheduled_at: new Date(Date.now() + 259200000).toISOString(), created_at: new Date().toISOString(), status: "pending" },
    ],
  },
};

export const Empty: Story = {
  args: { posts: [] },
};

export const Loading: Story = {
  args: { isLoading: true },
};
