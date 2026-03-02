"use client";

import { useEffect, useRef } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { RefreshCw } from "lucide-react";
import type { BlogPost, LinkedInFields } from "@/lib/types";

interface LinkedInControlsProps {
  fields: LinkedInFields;
  onChange: (fields: LinkedInFields) => void;
  blogPosts: BlogPost[];
  analyticsConfigured: boolean;
  isLoadingPosts: boolean;
  onFetchPosts: (days: number) => void;
  onRefresh: () => void;
}

export function LinkedInControls({
  fields,
  onChange,
  blogPosts,
  analyticsConfigured,
  isLoadingPosts,
  onFetchPosts,
  onRefresh,
}: LinkedInControlsProps) {
  const update = <K extends keyof LinkedInFields>(key: K, value: LinkedInFields[K]) => {
    onChange({ ...fields, [key]: value });
  };

  // Fetch posts once on mount and when time range changes
  const lastFetchedRange = useRef<number | null>(null);
  useEffect(() => {
    if (analyticsConfigured && lastFetchedRange.current !== fields.timeRange) {
      lastFetchedRange.current = fields.timeRange;
      onFetchPosts(fields.timeRange);
    }
  }, [fields.timeRange, analyticsConfigured, onFetchPosts]);

  // Deduplicate blog posts by URL (GA4 can return duplicates)
  const uniquePosts = blogPosts.reduce<BlogPost[]>((acc, post) => {
    if (!acc.some((p) => p.url === post.url)) {
      acc.push(post);
    }
    return acc;
  }, []);

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>Time Range</Label>
        <Select
          value={String(fields.timeRange)}
          onValueChange={(v) => update("timeRange", Number(v))}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="60">Last 60 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>Blog Post</Label>
          {analyticsConfigured && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRefresh}
              disabled={isLoadingPosts}
              className="h-6 px-2"
            >
              <RefreshCw className={`h-3 w-3 ${isLoadingPosts ? "animate-spin" : ""}`} />
            </Button>
          )}
        </div>

        {analyticsConfigured && uniquePosts.length > 0 ? (
          <Select
            value={fields.blogUrl}
            onValueChange={(v) => update("blogUrl", v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select a blog post" />
            </SelectTrigger>
            <SelectContent>
              {uniquePosts.map((post, i) => (
                <SelectItem key={`${post.url}-${i}`} value={post.url}>
                  {post.title} ({post.views} views)
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ) : (
          <Input
            value={fields.blogUrl}
            onChange={(e) => update("blogUrl", e.target.value)}
            placeholder={
              analyticsConfigured && isLoadingPosts
                ? "Loading blog posts..."
                : analyticsConfigured
                  ? "No blog posts found"
                  : "Paste blog URL (GA4 not configured)"
            }
          />
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>Post Count</Label>
          <span className="text-sm text-muted-foreground">{fields.postCount}</span>
        </div>
        <Slider
          value={[fields.postCount]}
          onValueChange={([v]) => update("postCount", v)}
          min={1}
          max={5}
          step={1}
        />
      </div>
    </div>
  );
}
