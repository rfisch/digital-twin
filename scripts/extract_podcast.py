"""Extract and clean podcast transcripts from data/raw/podcasts/.

Supports:
- Plain text transcripts (.txt)
- SRT/VTT subtitle files (.srt, .vtt)
- JSON transcripts from common services (.json) — Otter.ai, Descript, Whisper, etc.

Podcast transcripts are conversational, so this script:
1. Extracts Jacq's speech (filters by speaker if labeled)
2. Cleans filler words and transcript artifacts
3. Outputs cleaned text to data/processed/podcasts/
"""

import json
import re
import sys
from pathlib import Path


RAW_DIR = Path("data/raw/podcasts")
OUTPUT_DIR = Path("data/processed/podcasts")

# Common filler words/sounds to optionally remove
FILLERS = re.compile(
    r"\b(um+|uh+|hmm+|ah+|er+|like,?\s(?=like)|you know,?\s(?=you know))"
    r"(?:\s|,\s?)",
    re.IGNORECASE,
)


def extract_txt(path: Path) -> str:
    """Extract from a plain text transcript."""
    return path.read_text(encoding="utf-8")


def extract_srt(path: Path) -> str:
    """Extract text from an SRT subtitle file."""
    text = path.read_text(encoding="utf-8")
    lines = []
    for block in re.split(r"\n\n+", text):
        block_lines = block.strip().split("\n")
        # SRT blocks: index, timestamp, text (1+ lines)
        # Skip index line and timestamp line
        content_lines = [
            l for l in block_lines
            if not re.match(r"^\d+$", l.strip())
            and not re.match(r"\d{2}:\d{2}:\d{2}", l.strip())
        ]
        if content_lines:
            # Strip HTML-like tags from SRT
            cleaned = " ".join(content_lines)
            cleaned = re.sub(r"<[^>]+>", "", cleaned)
            lines.append(cleaned.strip())
    return " ".join(lines)


def extract_vtt(path: Path) -> str:
    """Extract text from a WebVTT subtitle file."""
    text = path.read_text(encoding="utf-8")
    lines = []
    for block in re.split(r"\n\n+", text):
        block_lines = block.strip().split("\n")
        content_lines = [
            l for l in block_lines
            if not l.startswith("WEBVTT")
            and not l.startswith("NOTE")
            and not re.match(r"\d{2}:\d{2}:\d{2}\.\d{3}\s*-->", l.strip())
            and not re.match(r"^\d+$", l.strip())
        ]
        if content_lines:
            cleaned = " ".join(content_lines)
            cleaned = re.sub(r"<[^>]+>", "", cleaned)
            lines.append(cleaned.strip())
    return " ".join(lines)


def extract_json_transcript(path: Path) -> str:
    """Extract from JSON transcript (Otter.ai, Descript, Whisper, etc.).

    Tries to detect the format and extract speaker-labeled segments.
    Returns all text, with speaker labels preserved for later filtering.
    """
    data = json.loads(path.read_text(encoding="utf-8"))

    # Whisper format: {"text": "...", "segments": [{"text": "..."}]}
    if isinstance(data, dict) and "segments" in data:
        segments = data["segments"]
        parts = []
        for seg in segments:
            text = seg.get("text", "").strip()
            speaker = seg.get("speaker", "")
            if text:
                if speaker:
                    parts.append(f"[{speaker}]: {text}")
                else:
                    parts.append(text)
        return "\n".join(parts)

    # Otter.ai format: {"transcription": [{"speaker": "...", "text": "..."}]}
    if isinstance(data, dict) and "transcription" in data:
        parts = []
        for seg in data["transcription"]:
            text = seg.get("text", "").strip()
            speaker = seg.get("speaker", "")
            if text:
                prefix = f"[{speaker}]: " if speaker else ""
                parts.append(f"{prefix}{text}")
        return "\n".join(parts)

    # Descript format: {"paragraphs": [{"speaker": "...", "lines": [...]}]}
    if isinstance(data, dict) and "paragraphs" in data:
        parts = []
        for para in data["paragraphs"]:
            speaker = para.get("speaker", "")
            lines = para.get("lines", [])
            text = " ".join(
                word.get("text", "") for line in lines
                for word in (line.get("words", []) if isinstance(line, dict) else [])
            ).strip()
            if not text and isinstance(lines, list):
                text = " ".join(str(l) for l in lines).strip()
            if text:
                prefix = f"[{speaker}]: " if speaker else ""
                parts.append(f"{prefix}{text}")
        return "\n".join(parts)

    # Generic: just dump any string values we find
    if isinstance(data, list):
        parts = []
        for item in data:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text", item.get("content", ""))
                speaker = item.get("speaker", item.get("name", ""))
                if text:
                    prefix = f"[{speaker}]: " if speaker else ""
                    parts.append(f"{prefix}{text}")
        return "\n".join(parts)

    return str(data)


def filter_speaker(text: str, speaker_names: list[str] | None = None) -> str:
    """Filter transcript to only include lines from specific speakers.

    If speaker_names is None, returns all text with speaker labels stripped.
    Speaker labels expected as [Speaker Name]: text
    """
    lines = text.split("\n")
    filtered = []

    for line in lines:
        match = re.match(r"^\[([^\]]+)\]:\s*(.*)", line)
        if match:
            speaker, content = match.group(1), match.group(2)
            if speaker_names is None or any(
                name.lower() in speaker.lower() for name in speaker_names
            ):
                filtered.append(content.strip())
        else:
            # Unlabeled line — include if no speaker filter
            if speaker_names is None:
                filtered.append(line.strip())

    return "\n\n".join(line for line in filtered if line)


def clean_transcript(text: str, remove_fillers: bool = True) -> str:
    """Clean transcript text."""
    # Remove timestamps like [00:12:34] or (00:12:34)
    text = re.sub(r"[\[\(]\d{1,2}:\d{2}(?::\d{2})?[\]\)]", "", text)

    # Remove filler words if requested
    if remove_fillers:
        text = FILLERS.sub("", text)

    # Collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Clean up punctuation artifacts
    text = re.sub(r"\s+([.,!?])", r"\1", text)
    text = re.sub(r"([.,!?])([A-Z])", r"\1 \2", text)

    return text.strip()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract podcast transcripts")
    parser.add_argument(
        "--speaker",
        nargs="*",
        default=None,
        help="Filter to these speaker names (e.g., --speaker Jacq 'Jacqueline'). "
             "If not set, includes all speakers.",
    )
    parser.add_argument(
        "--keep-fillers",
        action="store_true",
        help="Keep filler words (um, uh, like, you know)",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not RAW_DIR.exists():
        print(f"Directory {RAW_DIR}/ not found.")
        sys.exit(1)

    extractors = {
        ".txt": extract_txt,
        ".srt": extract_srt,
        ".vtt": extract_vtt,
        ".json": extract_json_transcript,
    }

    files = []
    for ext, extractor in extractors.items():
        files.extend((f, extractor) for f in RAW_DIR.glob(f"*{ext}"))

    if not files:
        print(f"No transcript files found in {RAW_DIR}/")
        print("Supported formats: .txt, .srt, .vtt, .json")
        sys.exit(0)

    print(f"Processing {len(files)} transcript files...")
    if args.speaker:
        print(f"Filtering to speakers: {', '.join(args.speaker)}")

    for file_path, extractor in sorted(files):
        print(f"  Extracting: {file_path.name}")

        raw_text = extractor(file_path)
        text = filter_speaker(raw_text, args.speaker)
        text = clean_transcript(text, remove_fillers=not args.keep_fillers)

        if not text.strip():
            print(f"    Skipped (no matching content)")
            continue

        output_path = OUTPUT_DIR / f"{file_path.stem}.txt"
        # Add metadata header
        content = f"TITLE: {file_path.stem.replace('-', ' ').replace('_', ' ').title()}\n"
        content += f"SOURCE: podcast\n\n{text}"
        output_path.write_text(content, encoding="utf-8")
        print(f"    → {output_path} ({len(text):,} chars)")

    print(f"\nDone. Extracted to {OUTPUT_DIR}/")
    print("Next: python scripts/clean_text.py")


if __name__ == "__main__":
    main()
