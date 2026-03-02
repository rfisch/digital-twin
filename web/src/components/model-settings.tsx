"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Info } from "lucide-react";

interface ModelSettingsProps {
  model: string;
  onModelChange: (value: string) => void;
  temperature: number;
  onTemperatureChange: (value: number) => void;
  maxTokens: number;
  onMaxTokensChange: (value: number) => void;
  useRag: boolean;
  onUseRagChange: (value: boolean) => void;
  availableModels: string[];
}

function Tooltip({ text }: { text: string }) {
  return (
    <span className="group relative inline-flex ml-1 cursor-help">
      <Info className="h-3.5 w-3.5 text-muted-foreground" />
      <span className="pointer-events-none absolute left-full top-1/2 -translate-y-1/2 ml-2 w-56 rounded bg-popover border px-3 py-2 text-xs text-popover-foreground opacity-0 shadow-md transition-opacity group-hover:opacity-100 z-50">
        {text}
      </span>
    </span>
  );
}

// Default models to always show, even if Ollama isn't running
const FALLBACK_MODELS = ["jacq-v6:8b", "llama3.1:8b"];

export function ModelSettings({
  model,
  onModelChange,
  temperature,
  onTemperatureChange,
  maxTokens,
  onMaxTokensChange,
  useRag,
  onUseRagChange,
  availableModels,
}: ModelSettingsProps) {
  // Merge available models with fallback defaults
  const models = availableModels.length > 0
    ? availableModels
    : FALLBACK_MODELS;

  // Ensure current model is always in the list
  const allModels = models.includes(model) ? models : [model, ...models];

  return (
    <Accordion type="single" collapsible>
      <AccordionItem value="model-settings">
        <AccordionTrigger className="text-sm font-medium">
          Model Settings
        </AccordionTrigger>
        <AccordionContent className="space-y-4 pt-2">
          <div className="space-y-2">
            <div className="flex items-center">
              <Label htmlFor="model">Model</Label>
              <Tooltip text="The fine-tuned model used for generation. jacq-v6:8b is Jacq's voice model. llama3.1:8b is the untuned baseline for comparison." />
            </div>
            <Select value={model} onValueChange={onModelChange}>
              <SelectTrigger id="model">
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent>
                {allModels.map((m) => (
                  <SelectItem key={m} value={m}>
                    {m}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Label>Temperature</Label>
                <Tooltip text="Controls randomness. Lower (0.3-0.5) = more focused and predictable. Higher (0.7-1.0) = more creative and varied. LinkedIn posts use 0.6 by default to reduce hallucination." />
              </div>
              <span className="text-sm text-muted-foreground">{temperature.toFixed(1)}</span>
            </div>
            <Slider
              value={[temperature]}
              onValueChange={([v]) => onTemperatureChange(v)}
              min={0}
              max={1.5}
              step={0.1}
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Label>Max Tokens</Label>
                <Tooltip text="Maximum length of generated text. 512 tokens is roughly a short LinkedIn post. 2048 is a full blog post. Higher values allow longer output but take more time." />
              </div>
              <span className="text-sm text-muted-foreground">{maxTokens}</span>
            </div>
            <Slider
              value={[maxTokens]}
              onValueChange={([v]) => onMaxTokensChange(v)}
              min={256}
              max={4096}
              step={256}
            />
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="use-rag"
              checked={useRag}
              onCheckedChange={(checked) => onUseRagChange(checked === true)}
            />
            <Label htmlFor="use-rag" className="text-sm font-normal">
              Use RAG
            </Label>
            <Tooltip text="Retrieval-augmented generation. OFF by default — RAG hurts voice quality for creative writing. Only enable for factual lookups (specific dates, names, events from Jacq's work)." />
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
