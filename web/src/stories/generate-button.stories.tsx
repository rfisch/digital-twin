import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { GenerateButton } from "@/components/generate-button";

const meta: Meta<typeof GenerateButton> = {
  title: "Components/GenerateButton",
  component: GenerateButton,
  args: {
    onClick: () => {},
    isLoading: false,
  },
};
export default meta;

type Story = StoryObj<typeof GenerateButton>;

export const Default: Story = {};
export const Loading: Story = { args: { isLoading: true } };
