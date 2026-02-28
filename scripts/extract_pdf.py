"""Extract text from PDF files in data/raw/books/."""

import sys
from pathlib import Path

import pymupdf  # PyMuPDF


RAW_DIR = Path("data/raw/books")
OUTPUT_DIR = Path("data/processed")


def extract_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file, preserving paragraph structure."""
    doc = pymupdf.open(pdf_path)
    pages = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            pages.append(text)
    doc.close()
    return "\n\n".join(pages)


def clean_extracted_text(text: str) -> str:
    """Basic cleanup of PDF-extracted text."""
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip page numbers (standalone digits)
        if stripped.isdigit():
            continue
        # Skip very short lines that are likely headers/footers
        if len(stripped) < 3 and not stripped:
            continue
        cleaned.append(stripped)

    # Rejoin lines, collapsing single newlines (PDF line breaks within paragraphs)
    # but preserving double newlines (paragraph breaks)
    result = []
    for line in cleaned:
        if not line:
            result.append("")
        elif result and result[-1]:
            # If previous line was non-empty, this might be a continuation
            result[-1] += " " + line
        else:
            result.append(line)

    return "\n\n".join(line for line in result if line)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {RAW_DIR}/")
        print("Place PDF files there and re-run.")
        sys.exit(0)

    for pdf_path in pdf_files:
        print(f"Extracting: {pdf_path.name}")
        raw_text = extract_pdf(pdf_path)
        cleaned = clean_extracted_text(raw_text)

        output_path = OUTPUT_DIR / f"{pdf_path.stem}.txt"
        output_path.write_text(cleaned, encoding="utf-8")
        print(f"  → {output_path} ({len(cleaned):,} chars)")

    print(f"\nDone. Extracted {len(pdf_files)} PDF(s) to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
