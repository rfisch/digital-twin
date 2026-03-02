import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { SchedulePicker } from "@/components/schedule-picker";

const meta: Meta<typeof SchedulePicker> = {
  title: "Components/SchedulePicker",
  component: SchedulePicker,
  args: {
    value: null,
    onChange: () => {},
  },
};
export default meta;

type Story = StoryObj<typeof SchedulePicker>;

export const Default: Story = {};

export const WithDate: Story = {
  args: {
    value: new Date(Date.now() + 86400000).toISOString(),
  },
};
