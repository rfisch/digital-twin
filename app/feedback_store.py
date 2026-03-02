"""Append-only JSONL store for edit tracking preference pairs.

Saves original model output vs. what Jacqueline actually sends,
building a dataset for future DPO/preference training.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_PATH = Path(__file__).parent.parent / "data" / "feedback" / "edits.jsonl"


class FeedbackStore:
    """Append-only JSONL store for generation/edit pairs."""

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else DEFAULT_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, record: dict) -> str:
        """Append one record to the JSONL file. Returns the record UUID."""
        record_id = str(uuid.uuid4())
        record = {
            "id": record_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **record,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record_id

    def load_all(self) -> list[dict]:
        """Read all records from the JSONL file."""
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
        return records
