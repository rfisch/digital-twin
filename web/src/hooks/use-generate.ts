"use client";

import { useState, useCallback } from "react";
import { generate, generateLinkedInMulti } from "@/lib/api";
import type {
  TaskType,
  GenerateRequest,
  GenerateResponse,
  PostResult,
  EmailFields,
  EmailReplyFields,
  CopywritingFields,
} from "@/lib/types";

interface UseGenerateReturn {
  generateSingle: (params: {
    taskType: TaskType;
    topic: string;
    model: string;
    temperature: number;
    maxTokens: number;
    useRag: boolean;
    emailFields?: EmailFields;
    emailReplyFields?: EmailReplyFields;
    copywritingFields?: CopywritingFields;
  }) => Promise<PostResult | null>;
  generateLinkedIn: (params: {
    blogUrl: string;
    count: number;
    model: string;
    temperature: number;
    maxTokens: number;
  }) => Promise<PostResult[] | null>;
  isLoading: boolean;
  error: string | null;
}

export function useGenerate(): UseGenerateReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateSingle = useCallback(
    async (params: {
      taskType: TaskType;
      topic: string;
      model: string;
      temperature: number;
      maxTokens: number;
      useRag: boolean;
      emailFields?: EmailFields;
      emailReplyFields?: EmailReplyFields;
      copywritingFields?: CopywritingFields;
    }): Promise<PostResult | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const req: GenerateRequest = {
          task_type: params.taskType,
          topic: params.topic,
          model: params.model,
          temperature: params.temperature,
          max_tokens: params.maxTokens,
          use_rag: params.useRag,
        };

        // Add task-specific fields
        if (params.emailFields) {
          req.recipient = params.emailFields.recipient;
          req.purpose = params.emailFields.purpose;
          req.email_type = params.emailFields.emailType;
        }
        if (params.emailReplyFields) {
          req.received_email = params.emailReplyFields.receivedEmail;
          req.sender_name = params.emailReplyFields.senderName;
          req.sender_email = params.emailReplyFields.senderEmail;
          req.subject = params.emailReplyFields.subject;
          req.goal = params.emailReplyFields.goal;
          req.tone_notes = params.emailReplyFields.toneNotes;
        }
        if (params.copywritingFields) {
          req.medium = params.copywritingFields.medium;
          req.audience = params.copywritingFields.audience;
          req.message = params.copywritingFields.message;
          req.tone = params.copywritingFields.tone;
        }

        const res: GenerateResponse = await generate(req);
        return {
          text: res.text,
          originalText: res.text,
          promptInfo: res.prompt_info,
        };
      } catch (err) {
        const message = err instanceof Error ? err.message : "Generation failed";
        setError(message);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const generateLinkedIn = useCallback(
    async (params: {
      blogUrl: string;
      count: number;
      model: string;
      temperature: number;
      maxTokens: number;
    }): Promise<PostResult[] | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const res = await generateLinkedInMulti({
          blog_url: params.blogUrl,
          count: params.count,
          model: params.model,
          temperature: params.temperature,
          max_tokens: params.maxTokens,
        });

        return res.posts.map((p) => ({
          text: p.text,
          originalText: p.text,
          promptInfo: p.prompt_info,
        }));
      } catch (err) {
        const message = err instanceof Error ? err.message : "Generation failed";
        setError(message);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  return { generateSingle, generateLinkedIn, isLoading, error };
}
