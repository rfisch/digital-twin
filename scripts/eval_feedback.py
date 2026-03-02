#!/usr/bin/env python3
"""Assess training readiness: feedback pairs + new blog content.

Checks two data sources for retraining signals:
1. Feedback pairs (data/feedback/edits.jsonl) — edited generation outputs
2. New blog posts on jacquelinefisch.com and substack — fresh training content

Usage: .venv/bin/python scripts/eval_feedback.py
       .venv/bin/python scripts/eval_feedback.py --skip-scrape  # offline mode
"""

import argparse
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.feedback_store import FeedbackStore
from scripts.build_exemplars import score_jacqness
from scripts.build_training_data import PRIMARY_BUZZWORDS, EXTENDED_BUZZWORDS


# ---------- config ----------

PROCESSED_DIR = Path("data/processed/blog")
TRAINING_FILE = Path("data/training/train.jsonl")

# Thresholds
MIN_FEEDBACK_PAIRS = 25
NEW_POSTS_THRESHOLD = 10  # new blog posts worth a retrain on their own

SQUARESPACE_BASE = "https://theintuitivewritingschool.com"
SUBSTACK_BASE = "https://jacquelinefisch.substack.com"


# ---------- helpers ----------

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(html: str) -> str:
    """Remove HTML tags, returning plain text."""
    return _TAG_RE.sub("", html).strip()


def normalized_levenshtein(a: str, b: str) -> float:
    """Normalized Levenshtein distance (0 = identical, 1 = total rewrite)."""
    if a == b:
        return 0.0
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return 1.0
    # Standard DP — fine for the text sizes we'll see
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [i] + [0] * m
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = curr
    return prev[m] / max(n, m)


def count_buzzwords(text: str) -> int:
    """Count all buzzword occurrences (primary + extended)."""
    text_lower = text.lower()
    total = 0
    for bw in PRIMARY_BUZZWORDS | EXTENDED_BUZZWORDS:
        total += text_lower.count(bw)
    return total


# ---------- per-pair analysis ----------

def analyze_pair(record: dict) -> dict | None:
    """Compute metrics for one feedback pair. Returns None if unusable."""
    original_html = record.get("original_output", "")
    edited_html = record.get("edited_output", "")

    original = strip_html(original_html)
    edited = strip_html(edited_html)

    word_count = len(edited.split())
    if word_count < 50:
        return None

    edit_dist = normalized_levenshtein(original, edited)

    jacq_orig = score_jacqness(original)
    jacq_edit = score_jacqness(edited)
    jacq_delta = jacq_edit["total"] - jacq_orig["total"]

    buzz_orig = count_buzzwords(original)
    buzz_edit = count_buzzwords(edited)
    buzz_delta = buzz_edit - buzz_orig

    return {
        "id": record.get("id", "?"),
        "edit_distance": round(edit_dist, 4),
        "jacq_score_original": jacq_orig["total"],
        "jacq_score_edited": jacq_edit["total"],
        "jacq_delta": round(jacq_delta, 2),
        "buzzword_count_original": buzz_orig,
        "buzzword_count_edited": buzz_edit,
        "buzzword_delta": buzz_delta,
        "word_count": word_count,
        "was_edited": record.get("was_edited", False),
        "was_sent": record.get("was_sent", False),
    }


# ---------- new blog post detection ----------

def _normalize_title(title: str) -> str:
    t = title.lower().strip()
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t)
    return t


def _content_fingerprint(text: str) -> str:
    words = re.sub(r"[^\w\s]", "", text.lower()).split()[:100]
    return " ".join(words)


def _existing_posts() -> tuple[set[str], set[str], set[str]]:
    """Get slugs, titles, and fingerprints of already-processed posts."""
    slugs, titles, fingerprints = set(), set(), set()
    if not PROCESSED_DIR.exists():
        return slugs, titles, fingerprints
    for f in PROCESSED_DIR.glob("*.txt"):
        slugs.add(f.stem)
        try:
            text = f.read_text(encoding="utf-8")
            lines = text.split("\n", 3)
            if lines[0].startswith("TITLE: "):
                titles.add(_normalize_title(lines[0][7:]))
            parts = text.split("\n\n", 1)
            body = parts[1] if len(parts) > 1 else ""
            if body.strip():
                fingerprints.add(_content_fingerprint(body))
        except Exception:
            pass
    return slugs, titles, fingerprints


def check_new_squarespace_posts(known_slugs, known_titles, known_fps) -> list[dict]:
    """Check Squarespace for new posts without downloading them."""
    import httpx

    new_posts = []
    offset = None

    try:
        client = httpx.Client(
            headers={"User-Agent": "Mozilla/5.0 (Macintosh)"},
            follow_redirects=True,
            timeout=15.0,
        )
    except Exception:
        return []

    try:
        for _ in range(20):  # max pages
            url = f"{SQUARESPACE_BASE}/blog?format=json"
            if offset:
                url += f"&offset={offset}"

            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            if not items:
                break

            for item in items:
                slug = item.get("urlId", "")
                title = item.get("title", "").strip()
                if not slug or not title:
                    continue

                fp = ""
                body_html = item.get("body", "")
                if body_html:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(body_html, "lxml")
                    body_text = soup.get_text(separator=" ")
                    if len(body_text.split()) < 100:
                        continue
                    fp = _content_fingerprint(body_text)

                if slug not in known_slugs and _normalize_title(title) not in known_titles and (not fp or fp not in known_fps):
                    publish_ms = item.get("publishOn", 0)
                    date_str = ""
                    if publish_ms:
                        dt = datetime.fromtimestamp(publish_ms / 1000, tz=timezone.utc)
                        date_str = dt.strftime("%Y-%m-%d")
                    new_posts.append({"title": title, "date": date_str, "source": "squarespace"})

            pagination = data.get("pagination", {})
            next_offset = pagination.get("nextPageOffset")
            if not next_offset or next_offset == offset:
                break
            offset = next_offset
            time.sleep(0.3)
    except Exception as e:
        print(f"  Warning: Squarespace check failed: {e}")
    finally:
        client.close()

    return new_posts


def check_new_substack_posts(known_slugs, known_titles, known_fps) -> list[dict]:
    """Check Substack archive for new posts."""
    import httpx

    new_posts = []

    try:
        client = httpx.Client(
            headers={"User-Agent": "Mozilla/5.0 (Macintosh)"},
            follow_redirects=True,
            timeout=15.0,
        )
    except Exception:
        return []

    try:
        resp = client.get(f"{SUBSTACK_BASE}/archive?sort=new")
        resp.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")

        for link in soup.select("a.post-preview-title"):
            title = link.get_text(strip=True)
            href = link.get("href", "")
            slug = href.rstrip("/").split("/")[-1] if href else ""

            if not title or not slug:
                continue

            if slug not in known_slugs and _normalize_title(title) not in known_titles:
                new_posts.append({"title": title, "date": "", "source": "substack"})
    except Exception as e:
        print(f"  Warning: Substack check failed: {e}")
    finally:
        client.close()

    return new_posts


# ---------- report ----------

def main():
    parser = argparse.ArgumentParser(description="Assess training readiness")
    parser.add_argument("--skip-scrape", action="store_true",
                        help="Skip checking websites for new blog posts (offline mode)")
    args = parser.parse_args()

    # --- Feedback pairs ---
    store = FeedbackStore()
    records = store.load_all()

    print("=" * 60)
    print("  Training Readiness Assessment")
    print("=" * 60)

    # Section 1: Feedback
    print()
    print("  --- Feedback Pairs ---")
    print()

    if not records:
        print("  No feedback pairs in data/feedback/edits.jsonl")
        feedback_ready = False
        quality_count = 0
    else:
        analyzed = []
        skipped = 0
        for rec in records:
            result = analyze_pair(rec)
            if result:
                analyzed.append(result)
            else:
                skipped += 1

        total = len(analyzed)
        meaningful = [p for p in analyzed if p["edit_distance"] > 0.05]
        sent = [p for p in analyzed if p["was_sent"]]
        quality = [
            p for p in analyzed
            if p["was_edited"] and p["was_sent"] and p["word_count"] >= 50
            and (p["jacq_delta"] > 0 or p["buzzword_delta"] < 0)
        ]

        print(f"  Total pairs collected:        {len(records)}")
        if skipped:
            print(f"  Skipped (too short):          {skipped}")
        print(f"  Usable pairs:                 {total}")
        print(f"  Meaningful edits (>5% diff):  {len(meaningful)}")
        print(f"  Actually sent:                {len(sent)}")

        if analyzed:
            mean_jacq = sum(p["jacq_delta"] for p in analyzed) / total
            mean_buzz = sum(p["buzzword_delta"] for p in analyzed) / total
            mean_edit = sum(p["edit_distance"] for p in analyzed) / total
            print()
            print(f"  Mean edit distance:           {mean_edit:.3f}")
            print(f"  Mean Jacq-ness delta:         {mean_jacq:+.2f}", end="")
            print("  (positive = edits improve voice)" if mean_jacq >= 0 else "  (negative = edits dilute voice)")
            print(f"  Mean buzzword delta:          {mean_buzz:+.2f}", end="")
            print("  (negative = edits reduce jargon)" if mean_buzz <= 0 else "  (positive = edits add jargon)")

        quality_count = len(quality)
        feedback_ready = quality_count >= MIN_FEEDBACK_PAIRS

    # Section 2: New blog posts
    print()
    print("  --- New Blog Content ---")
    print()

    training_date = ""
    if TRAINING_FILE.exists():
        mtime = TRAINING_FILE.stat().st_mtime
        training_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        training_count = sum(1 for _ in TRAINING_FILE.open())
        print(f"  Last training data built:     {training_date}")
        print(f"  Current training examples:    {training_count}")
    else:
        print("  No training data found")

    existing_count = len(list(PROCESSED_DIR.glob("*.txt"))) if PROCESSED_DIR.exists() else 0
    print(f"  Processed blog posts:         {existing_count}")

    new_posts = []
    if args.skip_scrape:
        print("  New post check:               skipped (--skip-scrape)")
        new_post_count = 0
    else:
        print("  Checking for new posts...")
        known_slugs, known_titles, known_fps = _existing_posts()
        sq_new = check_new_squarespace_posts(known_slugs, known_titles, known_fps)
        sub_new = check_new_substack_posts(known_slugs, known_titles, known_fps)
        new_posts = sq_new + sub_new
        new_post_count = len(new_posts)

        print(f"  New posts found:              {new_post_count}")
        if sq_new:
            print(f"    Squarespace:                {len(sq_new)}")
        if sub_new:
            print(f"    Substack:                   {len(sub_new)}")
        if new_posts:
            print()
            for p in new_posts[:10]:
                src = f"[{p['source'][:2].upper()}]"
                date = f" ({p['date']})" if p['date'] else ""
                print(f"    {src} {p['title']}{date}")
            if len(new_posts) > 10:
                print(f"    ... and {len(new_posts) - 10} more")

    content_ready = new_post_count >= NEW_POSTS_THRESHOLD

    # Section 3: Recommendation
    print()
    print("  --- Recommendation ---")
    print()

    reasons = []
    if feedback_ready:
        reasons.append(f"{quality_count} quality feedback pairs (>= {MIN_FEEDBACK_PAIRS})")
    if content_ready:
        reasons.append(f"{new_post_count} new blog posts (>= {NEW_POSTS_THRESHOLD})")

    if reasons:
        print("  READY TO RETRAIN")
        for r in reasons:
            print(f"    + {r}")
        print()
        print("  Next steps:")
        if content_ready:
            print("    1. make scrape-blog       # download new posts")
            print("    2. make data-pipeline     # rebuild training data")
        if feedback_ready:
            print("    3. Incorporate feedback pairs into training data")
        print(f"    {'3' if not feedback_ready else '4'}. make train              # train new adapter")
        print(f"    {'4' if not feedback_ready else '5'}. make evaluate           # evaluate new model")
    else:
        print("  NOT READY — keep collecting data")
        print()
        print(f"    Feedback pairs:  {quality_count}/{MIN_FEEDBACK_PAIRS} quality pairs")
        if not args.skip_scrape:
            print(f"    New blog posts:  {new_post_count}/{NEW_POSTS_THRESHOLD} new posts")
        print()
        print("  Either signal alone is enough to trigger a retrain.")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
