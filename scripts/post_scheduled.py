#!/usr/bin/env python3
"""Post scheduled LinkedIn content that is due.

Standalone script for cron:
    # Every 15 minutes
    */15 * * * * cd /Volumes/Code/jacq/digital-twin && .venv/bin/python scripts/post_scheduled.py >> logs/scheduler.log 2>&1

Or run manually:
    python scripts/post_scheduled.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.linkedin_client import LinkedInClient
from app.scheduler import PostScheduler


def main():
    scheduler = PostScheduler()
    linkedin = LinkedInClient()

    due = scheduler.get_due_posts()
    if not due:
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] Found {len(due)} due post(s)")

    if not linkedin.is_configured():
        print("  LinkedIn not configured — skipping all posts")
        for post in due:
            scheduler.mark_failed(post["id"], "LinkedIn not configured")
        return

    for post in due:
        print(f"  Posting {post['id'][:8]}... ", end="")
        try:
            result = linkedin.create_post(post["content"])
            if result.get("success"):
                scheduler.mark_posted(post["id"])
                print("OK")
            else:
                error = result.get("message", "Unknown error")
                scheduler.mark_failed(post["id"], error)
                print(f"FAILED: {error}")
        except Exception as e:
            scheduler.mark_failed(post["id"], str(e))
            print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
