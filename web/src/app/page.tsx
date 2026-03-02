"use client";

import { useState, useEffect, useCallback } from "react";
import { Header } from "@/components/header";
import { TaskSelector } from "@/components/task-selector";
import { TopicInput } from "@/components/topic-input";
import { ModelSettings } from "@/components/model-settings";
import { GenerateButton } from "@/components/generate-button";
import { OutputPanel } from "@/components/output-panel";
import { EmailFields } from "@/components/email-fields";
import { EmailReplyFields } from "@/components/email-reply-fields";
import { CopywritingFields } from "@/components/copywriting-fields";
import { LinkedInControls } from "@/components/linkedin-controls";
import { Toaster, toast } from "sonner";
import { useGenerate } from "@/hooks/use-generate";
import { useAnalytics } from "@/hooks/use-analytics";
import { useScheduler } from "@/hooks/use-scheduler";
import { getStatus, saveFeedback, postToLinkedIn, sendEmail } from "@/lib/api";
import { htmlToPlainText } from "@/components/rich-editor";
import {
  TASK_DEFAULTS,
  type TaskType,
  type PostResult,
  type EmailFields as EmailFieldsType,
  type EmailReplyFields as EmailReplyFieldsType,
  type CopywritingFields as CopywritingFieldsType,
  type LinkedInFields,
} from "@/lib/types";

export default function Home() {
  // --- Task & input state ---
  const [taskType, setTaskType] = useState<TaskType>("blog");
  const [topic, setTopic] = useState("");
  const [model, setModel] = useState("jacq-v6:8b");
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [useRag, setUseRag] = useState(false);

  // Task-specific fields
  const [emailFields, setEmailFields] = useState<EmailFieldsType>({
    recipient: "",
    purpose: "",
    emailType: "",
  });
  const [emailReplyFields, setEmailReplyFields] = useState<EmailReplyFieldsType>({
    receivedEmail: "",
    senderName: "",
    senderEmail: "",
    subject: "",
    goal: "",
    toneNotes: "",
  });
  const [copywritingFields, setCopywritingFields] = useState<CopywritingFieldsType>({
    medium: "",
    audience: "",
    message: "",
    tone: "",
  });
  const [linkedinFields, setLinkedinFields] = useState<LinkedInFields>({
    blogUrl: "",
    postCount: 3,
    timeRange: 30,
  });

  // --- Output state ---
  const [singleOutput, setSingleOutput] = useState<PostResult | null>(null);
  const [linkedinPosts, setLinkedinPosts] = useState<PostResult[]>([]);
  const [singleStatus, setSingleStatus] = useState("");
  const [linkedinPostStatuses, setLinkedinPostStatuses] = useState<Record<number, string>>({});
  const [linkedinPostScheduledAts, setLinkedinPostScheduledAts] = useState<Record<number, string | null>>({});

  // --- Service state ---
  const [gmailConfigured, setGmailConfigured] = useState(false);
  const [linkedinConfigured, setLinkedinConfigured] = useState(false);
  const [analyticsConfigured, setAnalyticsConfigured] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);

  // --- Hooks ---
  const { generateSingle, generateLinkedIn, isLoading, error } = useGenerate();
  const {
    blogPosts,
    isLoading: isLoadingPosts,
    fetchPosts,
    refresh: refreshPosts,
  } = useAnalytics();
  const {
    posts: scheduledPosts,
    isLoading: isLoadingScheduled,
    refresh: refreshScheduled,
    schedule,
    cancel: cancelScheduled,
    reschedule: rescheduleScheduled,
  } = useScheduler();

  // --- Fetch status on mount ---
  useEffect(() => {
    getStatus()
      .then((s) => {
        setGmailConfigured(s.gmail_configured);
        setLinkedinConfigured(s.linkedin_configured);
        setAnalyticsConfigured(s.analytics_configured);
        setAvailableModels(s.models);
      })
      .catch(() => {
        toast.error("Failed to connect to API server");
      });
  }, []);

  // --- Update defaults when task type changes ---
  const handleTaskTypeChange = useCallback((newType: TaskType) => {
    setTaskType(newType);
    const defaults = TASK_DEFAULTS[newType];
    setTemperature(defaults.temperature);
    setMaxTokens(defaults.maxTokens);
  }, []);

  // --- Show generation errors ---
  useEffect(() => {
    if (error) {
      toast.error(error);
    }
  }, [error]);

  // --- Generate handler ---
  const handleGenerate = useCallback(async () => {
    if (taskType === "linkedin") {
      if (!linkedinFields.blogUrl) {
        toast.error("Please select or enter a blog URL");
        return;
      }
      const results = await generateLinkedIn({
        blogUrl: linkedinFields.blogUrl,
        count: linkedinFields.postCount,
        model,
        temperature,
        maxTokens,
      });
      if (results) {
        setLinkedinPosts(results);
        setLinkedinPostStatuses({});
        toast.success(`Generated ${results.length} posts`);
      }
    } else {
      if (taskType !== "email_reply" && !topic) {
        toast.error("Please enter a topic");
        return;
      }
      if (taskType === "email_reply" && !emailReplyFields.receivedEmail) {
        toast.error("Please paste the received email");
        return;
      }
      const result = await generateSingle({
        taskType,
        topic,
        model,
        temperature,
        maxTokens,
        useRag,
        emailFields: taskType === "email" ? emailFields : undefined,
        emailReplyFields: taskType === "email_reply" ? emailReplyFields : undefined,
        copywritingFields: taskType === "copywriting" ? copywritingFields : undefined,
      });
      if (result) {
        setSingleOutput(result);
        setSingleStatus("");
        toast.success("Generated successfully");
      }
    }
  }, [
    taskType,
    topic,
    model,
    temperature,
    maxTokens,
    useRag,
    emailFields,
    emailReplyFields,
    copywritingFields,
    linkedinFields,
    generateSingle,
    generateLinkedIn,
  ]);

  // --- Keyboard shortcut: Cmd+Enter ---
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter" && !isLoading) {
        e.preventDefault();
        handleGenerate();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleGenerate, isLoading]);

  // --- Save feedback (edits) ---
  const handleSaveSingle = useCallback(async () => {
    if (!singleOutput) return;
    try {
      await saveFeedback({
        task_type: taskType,
        model,
        temperature,
        prompt: topic,
        original_output: singleOutput.originalText,
        edited_output: singleOutput.text,
        was_edited: singleOutput.text !== singleOutput.originalText,
        was_sent: false,
      });
      setSingleOutput({ ...singleOutput, originalText: singleOutput.text });
      setSingleStatus("Edits saved");
      toast.success("Edits saved");
    } catch {
      toast.error("Failed to save edits");
    }
  }, [singleOutput, taskType, model, temperature, topic]);

  const handleSaveLinkedIn = useCallback(
    async (index: number) => {
      const post = linkedinPosts[index];
      if (!post) return;
      try {
        await saveFeedback({
          task_type: "linkedin",
          model,
          temperature,
          prompt: linkedinFields.blogUrl,
          original_output: post.originalText,
          edited_output: post.text,
          was_edited: post.text !== post.originalText,
          was_sent: false,
        });
        const updated = [...linkedinPosts];
        updated[index] = { ...post, originalText: post.text };
        setLinkedinPosts(updated);
        setLinkedinPostStatuses((s) => ({ ...s, [index]: "Edits saved" }));
        toast.success(`Post ${index + 1} edits saved`);
      } catch {
        toast.error("Failed to save edits");
      }
    },
    [linkedinPosts, model, temperature, linkedinFields.blogUrl],
  );

  // --- Post to LinkedIn ---
  const handlePostLinkedIn = useCallback(
    async (text?: string, index?: number) => {
      const rawContent = text || singleOutput?.text;
      if (!rawContent) return;
      // Strip HTML — LinkedIn is text-only
      const content = htmlToPlainText(rawContent);
      try {
        const result = await postToLinkedIn(content);
        if (result.success) {
          if (index !== undefined) {
            setLinkedinPostStatuses((s) => ({ ...s, [index]: "Posted to LinkedIn" }));
          } else {
            setSingleStatus("Posted to LinkedIn");
          }
          toast.success("Posted to LinkedIn");
        } else {
          toast.error(result.message);
        }
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "Failed to post");
      }
    },
    [singleOutput],
  );

  // --- Send email ---
  const handleSendEmail = useCallback(async () => {
    if (!singleOutput?.text) return;
    const recipient = emailFields.recipient || emailReplyFields.senderEmail;
    const subject = emailReplyFields.subject || emailFields.purpose || "From Jacq";
    if (!recipient) {
      toast.error("No recipient email address");
      return;
    }
    try {
      const result = await sendEmail(recipient, subject, singleOutput.text);
      if (result.success) {
        setSingleStatus("Email sent");
        toast.success("Email sent");
      } else {
        toast.error(result.message);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to send email");
    }
  }, [singleOutput, emailFields, emailReplyFields]);

  // --- LinkedIn schedule ---
  const handleLinkedInSchedule = useCallback(
    async (index: number, scheduledAt: string) => {
      const post = linkedinPosts[index];
      if (!post) return;
      const plainText = htmlToPlainText(post.text);
      const id = await schedule(plainText, scheduledAt, linkedinFields.blogUrl);
      if (id) {
        setLinkedinPostScheduledAts((s) => ({ ...s, [index]: scheduledAt }));
        setLinkedinPostStatuses((s) => ({ ...s, [index]: `Scheduled (${id.slice(0, 8)})` }));
        toast.success(`Post ${index + 1} scheduled`);
      }
    },
    [linkedinPosts, schedule, linkedinFields.blogUrl],
  );

  const handleLinkedInCancelSchedule = useCallback(
    (index: number) => {
      setLinkedinPostScheduledAts((s) => ({ ...s, [index]: null }));
      setLinkedinPostStatuses((s) => {
        const next = { ...s };
        delete next[index];
        return next;
      });
      toast.info(`Post ${index + 1} schedule cancelled`);
    },
    [],
  );

  return (
    <div className="flex flex-col h-screen">
      <Header />

      <div className="flex flex-1 overflow-hidden">
        {/* Left column — Controls */}
        <div className="w-80 flex-shrink-0 border-r overflow-y-auto p-4 space-y-4">
          <TaskSelector value={taskType} onChange={handleTaskTypeChange} />

          {taskType !== "linkedin" && taskType !== "email_reply" && (
            <TopicInput value={topic} onChange={setTopic} taskType={taskType} />
          )}

          {taskType === "email" && (
            <EmailFields fields={emailFields} onChange={setEmailFields} />
          )}

          {taskType === "email_reply" && (
            <EmailReplyFields fields={emailReplyFields} onChange={setEmailReplyFields} />
          )}

          {taskType === "copywriting" && (
            <CopywritingFields fields={copywritingFields} onChange={setCopywritingFields} />
          )}

          {taskType === "linkedin" && (
            <LinkedInControls
              fields={linkedinFields}
              onChange={setLinkedinFields}
              blogPosts={blogPosts}
              analyticsConfigured={analyticsConfigured}
              isLoadingPosts={isLoadingPosts}
              onFetchPosts={fetchPosts}
              onRefresh={refreshPosts}
            />
          )}

          <ModelSettings
            model={model}
            onModelChange={setModel}
            temperature={temperature}
            onTemperatureChange={setTemperature}
            maxTokens={maxTokens}
            onMaxTokensChange={setMaxTokens}
            useRag={useRag}
            onUseRagChange={setUseRag}
            availableModels={availableModels}
          />

          <GenerateButton onClick={handleGenerate} isLoading={isLoading} />
        </div>

        {/* Right column — Output */}
        <div className="flex-1 overflow-y-auto p-6">
          <OutputPanel
            taskType={taskType}
            singleOutput={singleOutput}
            onSingleTextChange={(text) =>
              setSingleOutput((prev) => (prev ? { ...prev, text } : null))
            }
            onSingleSave={handleSaveSingle}
            onSendEmail={handleSendEmail}
            onPostLinkedIn={() => handlePostLinkedIn()}
            gmailConfigured={gmailConfigured}
            linkedinConfigured={linkedinConfigured}
            singleStatus={singleStatus}
            linkedinPosts={linkedinPosts}
            onLinkedInTextChange={(index, text) => {
              const updated = [...linkedinPosts];
              updated[index] = { ...updated[index], text };
              setLinkedinPosts(updated);
            }}
            onLinkedInSave={handleSaveLinkedIn}
            onLinkedInPostNow={(index) =>
              handlePostLinkedIn(linkedinPosts[index]?.text, index)
            }
            onLinkedInSchedule={handleLinkedInSchedule}
            onLinkedInCancelSchedule={handleLinkedInCancelSchedule}
            linkedinPostStatuses={linkedinPostStatuses}
            linkedinPostScheduledAts={linkedinPostScheduledAts}
            scheduledPosts={scheduledPosts}
            onRefreshScheduled={refreshScheduled}
            onCancelScheduled={cancelScheduled}
            onRescheduleScheduled={rescheduleScheduled}
            isLoadingScheduled={isLoadingScheduled}
          />
        </div>
      </div>

      <Toaster position="bottom-right" />
    </div>
  );
}
