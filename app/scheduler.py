"""Local scheduler for LinkedIn posts.

LinkedIn API has no scheduled posting support — lifecycleState: "PUBLISHED"
posts immediately. This module provides a simple JSON-backed scheduler that
a cron job (scripts/post_scheduled.py) checks periodically.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_PATH = Path(__file__).parent.parent / "data" / "scheduled_posts.json"


class PostScheduler:
    """Manage scheduled LinkedIn posts via a JSON file."""

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else DEFAULT_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            return []

    def _save(self, posts: list[dict]):
        self.path.write_text(
            json.dumps(posts, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def schedule(
        self,
        content: str,
        scheduled_at: float,
        source_url: str = "",
        feedback_id: str = "",
    ) -> str:
        """Add a post to the schedule. Returns schedule ID (uuid)."""
        schedule_id = str(uuid.uuid4())
        posts = self._load()
        posts.append({
            "id": schedule_id,
            "content": content,
            "scheduled_at": scheduled_at,
            "created_at": datetime.now(timezone.utc).timestamp(),
            "status": "pending",
            "posted_at": None,
            "error": None,
            "source_url": source_url,
            "feedback_id": feedback_id,
        })
        self._save(posts)
        return schedule_id

    def get_due_posts(self) -> list[dict]:
        """Posts where scheduled_at <= now and status == 'pending'."""
        now = datetime.now(timezone.utc).timestamp()
        return [
            p for p in self._load()
            if p["status"] == "pending" and p["scheduled_at"] <= now
        ]

    def mark_posted(self, schedule_id: str, posted_at: float | None = None):
        posts = self._load()
        for p in posts:
            if p["id"] == schedule_id:
                p["status"] = "posted"
                p["posted_at"] = posted_at or datetime.now(timezone.utc).timestamp()
                break
        self._save(posts)

    def mark_failed(self, schedule_id: str, error: str):
        posts = self._load()
        for p in posts:
            if p["id"] == schedule_id:
                p["status"] = "failed"
                p["error"] = error
                break
        self._save(posts)

    def cancel(self, schedule_id: str):
        """Cancel a pending scheduled post."""
        posts = self._load()
        for p in posts:
            if p["id"] == schedule_id:
                if p["status"] != "pending":
                    return
                p["status"] = "cancelled"
                break
        self._save(posts)

    def reschedule(self, schedule_id: str, new_time: float):
        """Change the scheduled time of a pending post."""
        posts = self._load()
        for p in posts:
            if p["id"] == schedule_id:
                if p["status"] != "pending":
                    return
                p["scheduled_at"] = new_time
                break
        self._save(posts)

    def get_pending(self) -> list[dict]:
        """All posts with status 'pending', sorted by scheduled_at."""
        pending = [p for p in self._load() if p["status"] == "pending"]
        pending.sort(key=lambda p: p["scheduled_at"])
        return pending

    def get_all(self) -> list[dict]:
        return self._load()
