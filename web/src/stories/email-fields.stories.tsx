import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { EmailFields } from "@/components/email-fields";

const meta: Meta<typeof EmailFields> = {
  title: "Components/EmailFields",
  component: EmailFields,
  args: {
    fields: { recipient: "", purpose: "", emailType: "" },
    onChange: () => {},
  },
};
export default meta;

type Story = StoryObj<typeof EmailFields>;

export const Default: Story = {};

export const FilledOut: Story = {
  args: {
    fields: {
      recipient: "Sarah Johnson",
      purpose: "Follow up on coaching proposal",
      emailType: "professional",
    },
  },
};
