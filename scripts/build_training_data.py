"""Build training data in chat JSONL format for MLX fine-tuning.

This is the most critical script in the pipeline. It converts Jacq's writing
into instruction-following chat format that teaches the model her voice.

Sources:
- Blog posts: real title → real post (natural prompt/response pairs)
- Book excerpts: chunks of text with generated prompts

Output: data/training/all.jsonl (before splitting)
"""

import json
import re
import sys
from pathlib import Path

import httpx


PROCESSED_DIR = Path("data/processed")
BLOG_DIR = PROCESSED_DIR / "blog"
TRAINING_DIR = Path("data/training")

SYSTEM_PROMPT_PATH = Path("prompts/system_prompt.txt")

# Ollama endpoint for prompt generation
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"


def load_system_prompt() -> str:
    """Load the system prompt for training examples."""
    if SYSTEM_PROMPT_PATH.exists():
        return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()
    return "You are Jacq. Write in her distinctive voice, matching her tone, rhythm, and style."


def build_blog_examples(system_prompt: str) -> list[dict]:
    """Build training examples from blog posts.

    Each blog post becomes one training example:
    - User message: "Write a blog post about {title}"
    - Assistant message: the actual blog post content
    """
    examples = []

    if not BLOG_DIR.exists():
        print("No blog directory found, skipping blog examples.")
        return examples

    blog_files = sorted(BLOG_DIR.glob("*.txt"))
    print(f"Processing {len(blog_files)} blog posts...")

    for blog_path in blog_files:
        text = blog_path.read_text(encoding="utf-8")

        # Extract title (first line should be "TITLE: ...")
        title = ""
        content = text
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("TITLE: "):
                title = line[7:].strip()
            elif line.startswith("DATE: "):
                continue
            elif line.strip():
                content = "\n".join(lines[i:]).strip()
                break

        if not title:
            title = blog_path.stem.replace("-", " ").title()

        if not content or len(content) < 100:
            print(f"  Skipping {blog_path.name} (too short)")
            continue

        # Vary the prompt format to avoid overfitting to one phrasing
        prompts = [
            f"Write a blog post about {title.lower()}",
            f"Write a blog post titled \"{title}\"",
            f"Write about {title.lower()} for the blog",
        ]
        # Use hash of title to deterministically pick a prompt variation
        prompt = prompts[hash(title) % len(prompts)]

        example = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": content},
            ]
        }
        examples.append(example)

    print(f"  Created {len(examples)} blog training examples")
    return examples


def chunk_text(text: str, min_words: int = 150, max_words: int = 800) -> list[str]:
    """Split text into chunks at paragraph boundaries."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = []
    current_words = 0

    for para in paragraphs:
        para_words = len(para.split())

        if current_words + para_words > max_words and current_words >= min_words:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_words = para_words
        else:
            current_chunk.append(para)
            current_words += para_words

    if current_chunk and current_words >= min_words:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def generate_prompt_for_passage(passage: str) -> str | None:
    """Use the local LLM to generate a plausible writing prompt for a passage.

    This makes book excerpts into instruction-following examples.
    """
    meta_prompt = (
        "Given the following passage of writing, generate a short writing prompt "
        "(1-2 sentences) that could have produced this text. The prompt should be "
        "a natural request someone might make, like 'Write about...' or "
        "'Describe...' or 'Reflect on...'. Return ONLY the prompt, nothing else.\n\n"
        f"Passage:\n{passage[:1500]}"
    )

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": meta_prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 100},
            },
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"  Warning: prompt generation failed: {e}")
        return None


def build_book_examples(system_prompt: str) -> list[dict]:
    """Build training examples from book text.

    Books are chunked into passages, then the LLM generates a plausible
    prompt for each passage.
    """
    examples = []

    # Find book text files (not in blog/ subdirectory)
    book_files = [
        f for f in PROCESSED_DIR.glob("*.txt")
        if f.name != "style_analysis.json"
    ]

    if not book_files:
        print("No book files found, skipping book examples.")
        return examples

    for book_path in book_files:
        print(f"Processing book: {book_path.name}")
        text = book_path.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        print(f"  Split into {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            prompt = generate_prompt_for_passage(chunk)
            if not prompt:
                # Fallback: generic prompt
                prompt = f"Write a passage in your voice about the themes in this section."

            example = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": chunk},
                ]
            }
            examples.append(example)

            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(chunks)} chunks")

    print(f"  Created {len(examples)} book training examples")
    return examples


def validate_examples(examples: list[dict]) -> list[dict]:
    """Validate and filter training examples."""
    valid = []
    for ex in examples:
        messages = ex.get("messages", [])
        if len(messages) != 3:
            continue
        if not all(m.get("content", "").strip() for m in messages):
            continue
        # Check assistant response has reasonable length
        assistant_content = messages[2]["content"]
        word_count = len(assistant_content.split())
        if word_count < 50:
            continue
        valid.append(ex)
    return valid


def main():
    TRAINING_DIR.mkdir(parents=True, exist_ok=True)

    system_prompt = load_system_prompt()
    print(f"System prompt: {len(system_prompt)} chars")
    print()

    all_examples = []

    # Blog posts (no LLM needed — natural prompt/response pairs)
    blog_examples = build_blog_examples(system_prompt)
    all_examples.extend(blog_examples)

    # Book excerpts (uses LLM to generate prompts)
    book_examples = build_book_examples(system_prompt)
    all_examples.extend(book_examples)

    if not all_examples:
        print("\nNo training examples generated!")
        print("Make sure you've run the extraction and cleaning scripts first:")
        print("  python scripts/extract_pdf.py")
        print("  python scripts/extract_docx.py")
        print("  python scripts/extract_blog.py")
        print("  python scripts/clean_text.py")
        sys.exit(1)

    # Validate
    valid_examples = validate_examples(all_examples)
    print(f"\nValidation: {len(valid_examples)}/{len(all_examples)} examples passed")

    # Write output
    output_path = TRAINING_DIR / "all.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for example in valid_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(valid_examples)} examples to {output_path}")
    print(f"Next step: python scripts/split_dataset.py")

    # Print summary
    word_counts = [
        len(ex["messages"][2]["content"].split()) for ex in valid_examples
    ]
    if word_counts:
        print(f"\nResponse length stats:")
        print(f"  Min: {min(word_counts)} words")
        print(f"  Max: {max(word_counts)} words")
        print(f"  Avg: {sum(word_counts) // len(word_counts)} words")


if __name__ == "__main__":
    main()
