"""Clean and normalize extracted text files.

Reads from data/processed/, applies cleaning, writes back in place.
Run after extraction scripts and before analyze_style.py.
"""

import re
import sys
from pathlib import Path


PROCESSED_DIR = Path("data/processed")
PODCAST_DIR = PROCESSED_DIR / "podcasts"


def clean_podcast_transcript(text: str) -> str:
    """Clean podcast transcript artifacts that dilute written voice.

    Removes filler words, back-channel responses, timestamps, and other
    spoken-word artifacts that shouldn't leak into training data.
    """
    # Remove timestamps like [00:12:34]
    text = re.sub(r"\[?\d{1,2}:\d{2}:\d{2}\]?", "", text)

    # Remove filler words (case-insensitive, word boundaries)
    # Match "um", "uh", "ah" as standalone or with trailing comma/period
    text = re.sub(r"\b[Uu][mh]\b[,.]?\s*", "", text)
    text = re.sub(r"\b[Aa]h\b[,.]?\s*", "", text)

    # Remove back-channel responses
    text = re.sub(r"\bMm-hmm\b\.?\s*", "", text)
    text = re.sub(r"\bUh-huh\b\.?\s*", "", text)
    text = re.sub(r"\bMm\b\.?\s*", "", text)

    # Remove standalone agreement lines (entire line is just the word)
    text = re.sub(r"(?m)^\s*(Yeah|Right|Totally|Exactly|Sure|Okay|OK)\.\s*$", "", text)

    # Remove repeated agreement patterns inline
    text = re.sub(r"\b(yeah,?\s*){2,}", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(right,?\s*){2,}", "", text, flags=re.IGNORECASE)

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove common show notes artifacts
    text = re.sub(r"(?m)^SEO Description:.*$", "", text)
    text = re.sub(r"(?m)^Links:\s*$", "", text)
    text = re.sub(r"(?m)^Podcast Show Notes:\s*$", "", text)

    # Clean up orphaned single-word lines (likely speaker labels or artifacts)
    text = re.sub(r"(?m)^\s*\w{1,3}\s*$", "", text)

    # Clean up resulting whitespace issues
    # Double spaces
    text = re.sub(r"  +", " ", text)
    # Space before punctuation
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    # Collapse 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove leading spaces on lines
    text = re.sub(r"(?m)^ +", "", text)

    return text.strip()


def clean_text(text: str) -> str:
    """Apply text cleaning and normalization."""
    # Normalize unicode quotes and dashes
    replacements = {
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2013": "-",   # en dash
        "\u2014": " - ", # em dash (with spaces)
        "\u2026": "...", # ellipsis
        "\u00a0": " ",   # non-breaking space
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Collapse multiple spaces (but preserve paragraph breaks)
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Remove common artifacts
    # Page numbers at start/end of paragraphs
    text = re.sub(r"(?m)^\d+\s*$", "", text)

    # Collapse any resulting triple+ newlines again
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def main():
    txt_files = list(PROCESSED_DIR.rglob("*.txt"))
    if not txt_files:
        print(f"No text files found in {PROCESSED_DIR}/")
        print("Run extraction scripts first.")
        sys.exit(0)

    total_chars_before = 0
    total_chars_after = 0

    for txt_path in txt_files:
        original = txt_path.read_text(encoding="utf-8")

        # Apply podcast-specific cleaning first for podcast files
        if PODCAST_DIR in txt_path.parents:
            cleaned = clean_podcast_transcript(original)
        else:
            cleaned = original

        # Apply general cleaning to all files
        cleaned = clean_text(cleaned)

        total_chars_before += len(original)
        total_chars_after += len(cleaned)

        txt_path.write_text(cleaned, encoding="utf-8")
        label = " [podcast]" if PODCAST_DIR in txt_path.parents else ""
        print(f"Cleaned{label}: {txt_path} ({len(original):,} → {len(cleaned):,} chars)")

    reduction = (1 - total_chars_after / total_chars_before) * 100 if total_chars_before else 0
    print(f"\nDone. Cleaned {len(txt_files)} files. "
          f"Size: {total_chars_before:,} → {total_chars_after:,} chars ({reduction:.1f}% reduction)")


if __name__ == "__main__":
    main()
