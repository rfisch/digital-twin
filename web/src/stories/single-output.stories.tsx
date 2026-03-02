import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { SingleOutput } from "@/components/single-output";

const meta: Meta<typeof SingleOutput> = {
  title: "Components/SingleOutput",
  component: SingleOutput,
  args: {
    result: {
      text: "There's something about mornings that I've never been able to fake my way through. Either you're a morning person or you're lying about it — and I spent years lying about it.\n\nBut here's what changed: I stopped trying to have a \"morning routine\" and started just... paying attention to what my body actually wanted at 6 AM. Spoiler: it wasn't a cold plunge.",
      originalText: "There's something about mornings that I've never been able to fake my way through. Either you're a morning person or you're lying about it — and I spent years lying about it.\n\nBut here's what changed: I stopped trying to have a \"morning routine\" and started just... paying attention to what my body actually wanted at 6 AM. Spoiler: it wasn't a cold plunge.",
      promptInfo: null,
    },
    taskType: "blog",
    onTextChange: () => {},
    onSave: () => {},
    onSendEmail: () => {},
    onPostLinkedIn: () => {},
    gmailConfigured: true,
    linkedinConfigured: true,
    status: "",
  },
};
export default meta;

type Story = StoryObj<typeof SingleOutput>;

export const BlogPost: Story = {};

export const EmailTask: Story = {
  args: { taskType: "email" },
};

export const EmailReply: Story = {
  args: {
    taskType: "email_reply",
    result: {
      text: "<p>Hi Sarah,</p><p>Thanks for reaching out — I'd love to chat about the coaching program.</p><p>Best,<br>Jacq</p>",
      originalText: "<p>Hi Sarah,</p><p>Thanks for reaching out — I'd love to chat about the coaching program.</p><p>Best,<br>Jacq</p>",
      promptInfo: null,
    },
  },
};

export const ServicesNotConfigured: Story = {
  args: { gmailConfigured: false, linkedinConfigured: false },
};

export const WithStatus: Story = {
  args: { status: "Edits saved" },
};

export const Edited: Story = {
  args: {
    result: {
      text: "The edited version with Jacq's corrections applied.",
      originalText: "The original generated version before edits.",
      promptInfo: null,
    },
  },
};
