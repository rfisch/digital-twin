import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useGenerate } from "@/hooks/use-generate";

vi.mock("@/lib/api", () => ({
  generate: vi.fn(),
  generateLinkedInMulti: vi.fn(),
}));

import { generate, generateLinkedInMulti } from "@/lib/api";

const mockGenerate = vi.mocked(generate);
const mockGenerateLinkedIn = vi.mocked(generateLinkedInMulti);

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useGenerate", () => {
  it("starts with isLoading false", () => {
    const { result } = renderHook(() => useGenerate());
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("generateSingle calls correct endpoint", async () => {
    mockGenerate.mockResolvedValueOnce({
      text: "Generated",
      prompt_info: { system: "s", user: "u" },
    });

    const { result } = renderHook(() => useGenerate());

    let output: ReturnType<typeof result.current.generateSingle> extends Promise<infer T> ? T : never;
    await act(async () => {
      output = await result.current.generateSingle({
        taskType: "blog",
        topic: "test",
        model: "jacq-v6:8b",
        temperature: 0.7,
        maxTokens: 2048,
        useRag: false,
      });
    });

    expect(mockGenerate).toHaveBeenCalledWith(
      expect.objectContaining({
        task_type: "blog",
        topic: "test",
      }),
    );
    expect(output!).toEqual({
      text: "Generated",
      originalText: "Generated",
      promptInfo: { system: "s", user: "u" },
    });
  });

  it("generateLinkedIn calls linkedin endpoint", async () => {
    mockGenerateLinkedIn.mockResolvedValueOnce({
      posts: [
        { text: "Post 1", prompt_info: null },
        { text: "Post 2", prompt_info: null },
      ],
    });

    const { result } = renderHook(() => useGenerate());

    let output: ReturnType<typeof result.current.generateLinkedIn> extends Promise<infer T> ? T : never;
    await act(async () => {
      output = await result.current.generateLinkedIn({
        blogUrl: "https://example.com",
        count: 2,
        model: "jacq-v6:8b",
        temperature: 0.6,
        maxTokens: 512,
      });
    });

    expect(mockGenerateLinkedIn).toHaveBeenCalledWith(
      expect.objectContaining({
        blog_url: "https://example.com",
        count: 2,
      }),
    );
    expect(output).toHaveLength(2);
  });

  it("sets error on failure", async () => {
    mockGenerate.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useGenerate());

    await act(async () => {
      const output = await result.current.generateSingle({
        taskType: "blog",
        topic: "test",
        model: "jacq-v6:8b",
        temperature: 0.7,
        maxTokens: 2048,
        useRag: false,
      });
      expect(output).toBeNull();
    });

    expect(result.current.error).toBe("Network error");
  });

  it("manages loading state", async () => {
    let resolveGenerate: (value: unknown) => void;
    const promise = new Promise((resolve) => {
      resolveGenerate = resolve;
    });
    mockGenerate.mockReturnValueOnce(promise as ReturnType<typeof generate>);

    const { result } = renderHook(() => useGenerate());

    let generatePromise: Promise<unknown>;
    act(() => {
      generatePromise = result.current.generateSingle({
        taskType: "blog",
        topic: "test",
        model: "jacq-v6:8b",
        temperature: 0.7,
        maxTokens: 2048,
        useRag: false,
      });
    });

    expect(result.current.isLoading).toBe(true);

    await act(async () => {
      resolveGenerate!({ text: "done", prompt_info: null });
      await generatePromise;
    });

    expect(result.current.isLoading).toBe(false);
  });
});
