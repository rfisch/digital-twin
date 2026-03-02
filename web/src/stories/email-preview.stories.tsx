import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { EmailPreview } from "@/components/email-preview";

const meta: Meta<typeof EmailPreview> = {
  title: "Components/EmailPreview",
  component: EmailPreview,
};
export default meta;

type Story = StoryObj<typeof EmailPreview>;

export const WithContent: Story = {
  args: {
    html: `<p>Hi Sarah,</p>
<p>Thank you for reaching out about the coaching program. I'd love to set up a time to chat more about what you're looking for and how we might work together.</p>
<p>I have some availability next week — would Tuesday or Thursday afternoon work for you?</p>
<p>Looking forward to connecting,<br>Jacq</p>`,
  },
};

export const Empty: Story = {
  args: { html: "" },
};
