"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import Placeholder from "@tiptap/extension-placeholder";
import { useRef } from "react";
import { Button } from "@/components/ui/button";
import {
  Bold,
  Italic,
  Underline as UnderlineIcon,
  List,
  ListOrdered,
  Heading2,
  Heading3,
  Undo,
  Redo,
  RemoveFormatting,
  Minus,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface RichEditorProps {
  content: string;
  onChange: (text: string) => void;
  placeholder?: string;
  minHeight?: string;
  className?: string;
}

function ToolbarButton({
  onClick,
  isActive,
  children,
  title,
}: {
  onClick: () => void;
  isActive?: boolean;
  children: React.ReactNode;
  title: string;
}) {
  return (
    <Button
      type="button"
      variant="ghost"
      size="sm"
      onClick={onClick}
      title={title}
      className={cn(
        "h-7 w-7 p-0",
        isActive && "bg-accent text-accent-foreground",
      )}
    >
      {children}
    </Button>
  );
}

/**
 * Convert plain text (with \n) to HTML paragraphs and line breaks.
 * Double newlines become paragraph breaks, single newlines become <br>.
 * If the string already looks like HTML (contains tags), return as-is.
 */
export function plainTextToHtml(text: string): string {
  if (!text) return "";
  // Already HTML — pass through
  if (/<[a-z][\s\S]*>/i.test(text)) return text;
  // Split on double newlines for paragraphs
  const paragraphs = text.split(/\n{2,}/);
  return paragraphs
    .map((p) => {
      const withBreaks = p
        .split("\n")
        .map((line) => line)
        .join("<br>");
      return `<p>${withBreaks}</p>`;
    })
    .join("");
}

/**
 * Extract plain text from HTML, preserving paragraph and line break structure.
 * <p> tags become double newlines, <br> tags become single newlines.
 */
export function htmlToPlainText(html: string): string {
  if (!html) return "";
  // If it doesn't look like HTML, return as-is
  if (!/<[a-z][\s\S]*>/i.test(html)) return html;

  if (typeof document === "undefined") {
    // SSR fallback
    return html
      .replace(/<br\s*\/?>/gi, "\n")
      .replace(/<\/p>\s*<p[^>]*>/gi, "\n\n")
      .replace(/<[^>]*>/g, "")
      .replace(/&nbsp;/g, " ")
      .replace(/&amp;/g, "&")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .trim();
  }

  // Use DOM for accurate extraction
  const div = document.createElement("div");
  div.innerHTML = html;

  let result = "";
  const walk = (node: Node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      result += node.textContent;
      return;
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return;

    const tag = (node as Element).tagName.toLowerCase();

    // Block elements get paragraph spacing
    if (tag === "p" || tag === "div" || tag === "h1" || tag === "h2" || tag === "h3" || tag === "h4") {
      if (result.length > 0 && !result.endsWith("\n\n")) {
        result += result.endsWith("\n") ? "\n" : "\n\n";
      }
    }
    if (tag === "br") {
      result += "\n";
      return;
    }
    if (tag === "li") {
      if (result.length > 0 && !result.endsWith("\n")) {
        result += "\n";
      }
      const parent = (node as Element).parentElement;
      if (parent && parent.tagName.toLowerCase() === "ol") {
        const idx = Array.from(parent.children).indexOf(node as Element) + 1;
        result += `${idx}. `;
      } else {
        result += "- ";
      }
    }
    if (tag === "hr") {
      result += "\n---\n";
      return;
    }

    for (const child of Array.from(node.childNodes)) {
      walk(child);
    }

    if (tag === "p" || tag === "div" || tag === "h1" || tag === "h2" || tag === "h3" || tag === "h4") {
      if (!result.endsWith("\n")) {
        result += "\n";
      }
    }
    if (tag === "ul" || tag === "ol") {
      if (!result.endsWith("\n")) {
        result += "\n";
      }
    }
  };

  walk(div);
  return result.replace(/\n{3,}/g, "\n\n").trim();
}

export function RichEditor({
  content,
  onChange,
  placeholder = "Start writing...",
  minHeight = "300px",
  className,
}: RichEditorProps) {
  // Guard against echoing our own onChange back as a setContent
  const suppressSync = useRef(false);
  // Track the last plain-text content we received externally
  const lastPlainText = useRef<string>("");

  const initialHtml = plainTextToHtml(content);

  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit.configure({
        heading: { levels: [2, 3] },
      }),
      Underline,
      Placeholder.configure({ placeholder }),
    ],
    content: initialHtml,
    onUpdate: ({ editor }) => {
      // User edited in the editor — propagate HTML up
      suppressSync.current = true;
      onChange(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: cn(
          "prose prose-sm max-w-none dark:prose-invert focus:outline-none px-3 py-2",
        ),
        style: `min-height: ${minHeight}`,
      },
    },
  });

  // When content prop changes (e.g. new generation), sync to editor.
  // We compare the plain-text representation to avoid spurious updates
  // from our own onChange echoing HTML back.
  const plainContent = htmlToPlainText(content);
  if (editor && plainContent !== lastPlainText.current) {
    if (suppressSync.current) {
      // This is our own onChange echoing back — skip the setContent
      suppressSync.current = false;
    } else {
      // Genuinely new external content (e.g. fresh generation)
      const html = plainTextToHtml(content);
      editor.commands.setContent(html, { emitUpdate: false });
    }
    lastPlainText.current = plainContent;
  }

  if (!editor) return null;

  return (
    <div className={cn("rounded-md border bg-background", className)}>
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-0.5 border-b px-1 py-1">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBold().run()}
          isActive={editor.isActive("bold")}
          title="Bold (Cmd+B)"
        >
          <Bold className="h-3.5 w-3.5" />
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleItalic().run()}
          isActive={editor.isActive("italic")}
          title="Italic (Cmd+I)"
        >
          <Italic className="h-3.5 w-3.5" />
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          isActive={editor.isActive("underline")}
          title="Underline (Cmd+U)"
        >
          <UnderlineIcon className="h-3.5 w-3.5" />
        </ToolbarButton>

        <div className="mx-1 h-4 w-px bg-border" />

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          isActive={editor.isActive("heading", { level: 2 })}
          title="Heading 2"
        >
          <Heading2 className="h-3.5 w-3.5" />
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          isActive={editor.isActive("heading", { level: 3 })}
          title="Heading 3"
        >
          <Heading3 className="h-3.5 w-3.5" />
        </ToolbarButton>

        <div className="mx-1 h-4 w-px bg-border" />

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          isActive={editor.isActive("bulletList")}
          title="Bullet List"
        >
          <List className="h-3.5 w-3.5" />
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          isActive={editor.isActive("orderedList")}
          title="Numbered List"
        >
          <ListOrdered className="h-3.5 w-3.5" />
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          title="Horizontal Rule"
        >
          <Minus className="h-3.5 w-3.5" />
        </ToolbarButton>

        <div className="mx-1 h-4 w-px bg-border" />

        <ToolbarButton
          onClick={() => editor.chain().focus().clearNodes().unsetAllMarks().run()}
          title="Clear Formatting"
        >
          <RemoveFormatting className="h-3.5 w-3.5" />
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().undo().run()}
          title="Undo (Cmd+Z)"
        >
          <Undo className="h-3.5 w-3.5" />
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().redo().run()}
          title="Redo (Cmd+Shift+Z)"
        >
          <Redo className="h-3.5 w-3.5" />
        </ToolbarButton>
      </div>

      {/* Editor Content */}
      <EditorContent editor={editor} />

      {/* Emoji hint */}
      <div className="border-t px-3 py-1.5 text-xs text-muted-foreground">
        Tip: Press <kbd className="rounded border bg-muted px-1 py-0.5 text-[10px] font-mono">Ctrl</kbd> + <kbd className="rounded border bg-muted px-1 py-0.5 text-[10px] font-mono">Cmd</kbd> + <kbd className="rounded border bg-muted px-1 py-0.5 text-[10px] font-mono">Space</kbd> to open the emoji picker. LinkedIn posts are text-only — formatting will be stripped.
      </div>
    </div>
  );
}
