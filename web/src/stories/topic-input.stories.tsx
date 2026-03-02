import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { TopicInput } from "@/components/topic-input";

const meta: Meta<typeof TopicInput> = {
  title: "Components/TopicInput",
  component: TopicInput,
  args: {
    value: "",
    onChange: () => {},
    taskType: "blog",
  },
};
export default meta;

type Story = StoryObj<typeof TopicInput>;

export const BlogPost: Story = { args: { taskType: "blog" } };
export const EmailTask: Story = { args: { taskType: "email" } };
export const CopywritingTask: Story = { args: { taskType: "copywriting" } };
export const FreeformTask: Story = { args: { taskType: "freeform" } };
export const WithContent: Story = {
  args: { taskType: "blog", value: "Write about morning routines and productivity" },
};
