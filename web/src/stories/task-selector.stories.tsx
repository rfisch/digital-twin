import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { TaskSelector } from "@/components/task-selector";

const meta: Meta<typeof TaskSelector> = {
  title: "Components/TaskSelector",
  component: TaskSelector,
  args: {
    value: "blog",
    onChange: () => {},
  },
};
export default meta;

type Story = StoryObj<typeof TaskSelector>;

export const Blog: Story = { args: { value: "blog" } };
export const Email: Story = { args: { value: "email" } };
export const EmailReply: Story = { args: { value: "email_reply" } };
export const Copywriting: Story = { args: { value: "copywriting" } };
export const LinkedIn: Story = { args: { value: "linkedin" } };
export const Freeform: Story = { args: { value: "freeform" } };
