"""Extract text from DOCX files in data/raw/books/."""

import sys
from pathlib import Path

from docx import Document


RAW_DIR = Path("data/raw/books")
OUTPUT_DIR = Path("data/processed")


def extract_docx(docx_path: Path) -> str:
    """Extract text from a DOCX file, preserving paragraph structure."""
    doc = Document(docx_path)
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    docx_files = list(RAW_DIR.glob("*.docx"))
    if not docx_files:
        print(f"No DOCX files found in {RAW_DIR}/")
        print("Place DOCX files there and re-run.")
        sys.exit(0)

    for docx_path in docx_files:
        print(f"Extracting: {docx_path.name}")
        text = extract_docx(docx_path)

        output_path = OUTPUT_DIR / f"{docx_path.stem}.txt"
        output_path.write_text(text, encoding="utf-8")
        print(f"  → {output_path} ({len(text):,} chars)")

    print(f"\nDone. Extracted {len(docx_files)} DOCX file(s) to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
