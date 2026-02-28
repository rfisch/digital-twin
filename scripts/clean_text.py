"""Clean and normalize extracted text files.

Reads from data/processed/, applies cleaning, writes back in place.
Run after extraction scripts and before analyze_style.py.
"""

import re
import sys
from pathlib import Path


PROCESSED_DIR = Path("data/processed")


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
        cleaned = clean_text(original)

        total_chars_before += len(original)
        total_chars_after += len(cleaned)

        txt_path.write_text(cleaned, encoding="utf-8")
        print(f"Cleaned: {txt_path} ({len(original):,} → {len(cleaned):,} chars)")

    reduction = (1 - total_chars_after / total_chars_before) * 100 if total_chars_before else 0
    print(f"\nDone. Cleaned {len(txt_files)} files. "
          f"Size: {total_chars_before:,} → {total_chars_after:,} chars ({reduction:.1f}% reduction)")


if __name__ == "__main__":
    main()
