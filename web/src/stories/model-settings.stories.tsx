import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { ModelSettings } from "@/components/model-settings";

const meta: Meta<typeof ModelSettings> = {
  title: "Components/ModelSettings",
  component: ModelSettings,
  args: {
    model: "jacq-v6:8b",
    onModelChange: () => {},
    temperature: 0.7,
    onTemperatureChange: () => {},
    maxTokens: 2048,
    onMaxTokensChange: () => {},
    useRag: false,
    onUseRagChange: () => {},
    availableModels: ["jacq-v6:8b", "llama3.1:8b"],
  },
};
export default meta;

type Story = StoryObj<typeof ModelSettings>;

export const Default: Story = {};

export const WithModelsLoaded: Story = {
  args: {
    availableModels: ["jacq-v6:8b", "llama3.1:8b", "jacq-v5:8b", "mistral:7b"],
  },
};

export const NoModelsAvailable: Story = {
  args: { availableModels: [] },
};

export const HighTemperature: Story = {
  args: { temperature: 1.2 },
};

export const RagEnabled: Story = {
  args: { useRag: true },
};
