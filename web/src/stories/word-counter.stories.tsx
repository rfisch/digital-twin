import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { WordCounter } from "@/components/word-counter";

const meta: Meta<typeof WordCounter> = {
  title: "Components/WordCounter",
  component: WordCounter,
  args: {
    text: "This is a sample text with several words in it.",
  },
};
export default meta;

type Story = StoryObj<typeof WordCounter>;

export const ShortText: Story = {
  args: { text: "Hello world" },
};

export const MediumText: Story = {
  args: { text: "This is a longer piece of text that has quite a few more words in it to demonstrate the word counter component working with medium-length content." },
};

export const NearLimit: Story = {
  args: { text: "x ".repeat(1490).trim() },
};

export const OverLimit: Story = {
  args: { text: "x ".repeat(1600).trim() },
};

export const Empty: Story = {
  args: { text: "" },
};

export const HtmlContent: Story = {
  args: {
    text: "<p>This is <strong>HTML</strong> content with <em>formatting</em>.</p>",
    isHtml: true,
  },
};
