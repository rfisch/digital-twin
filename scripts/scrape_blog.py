"""Scrape blog posts from Squarespace and Substack for training data.

Squarespace: Uses the JSON API at /blog?format=json (no HTML scraping needed).
Substack: Scrapes archive page to discover posts, then fetches each one.

Output format matches existing pipeline:
    TITLE: {title}
    DATE: {ISO date}

    {content}

Usage:
    python scripts/scrape_blog.py                        # scrape both
    python scripts/scrape_blog.py --source squarespace   # just the blog
    python scripts/scrape_blog.py --source substack      # just substack
    python scripts/scrape_blog.py --dry-run              # show what would be scraped
"""

import argparse
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

OUTPUT_DIR = Path("data/processed/blog")

SQUARESPACE_BASE = "https://theintuitivewritingschool.com"
SUBSTACK_BASE = "https://jacquelinefisch.substack.com"

RATE_LIMIT = 0.5  # seconds between requests
MIN_WORDS = 100


def make_client() -> httpx.Client:
    """Create an HTTP client with browser-like headers."""
    return httpx.Client(
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        },
        follow_redirects=True,
        timeout=30.0,
    )


def normalize_title(title: str) -> str:
    """Normalize a title for dedup comparison."""
    t = title.lower().strip()
    t = re.sub(r"[^\w\s]", "", t)  # strip punctuation
    t = re.sub(r"\s+", " ", t)  # collapse whitespace
    return t


def content_fingerprint(text: str) -> str:
    """Create a fingerprint from the first ~100 words of content for dedup."""
    words = re.sub(r"[^\w\s]", "", text.lower()).split()[:100]
    return " ".join(words)


def existing_posts() -> tuple[set[str], set[str], set[str]]:
    """Get slugs, normalized titles, and content fingerprints of processed files.

    Returns (slug_set, title_set, fingerprint_set) for robust dedup that
    catches retitled posts (Squarespace urlId != WordPress slug, and titles
    get SEO-updated over time).
    """
    slugs = set()
    titles = set()
    fingerprints = set()
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.glob("*.txt"):
            slugs.add(f.stem)
            try:
                text = f.read_text(encoding="utf-8")
                lines = text.split("\n", 3)
                # Extract title
                if lines[0].startswith("TITLE: "):
                    titles.add(normalize_title(lines[0][7:]))
                # Extract body (skip TITLE/DATE headers)
                body = ""
                for i, line in enumerate(lines):
                    if not line.startswith("TITLE:") and not line.startswith("DATE:") and line.strip():
                        body = text.split("\n", i)[1] if i > 0 else text
                        break
                if not body:
                    # Headers only, body starts after blank line
                    parts = text.split("\n\n", 1)
                    body = parts[1] if len(parts) > 1 else ""
                if body.strip():
                    fingerprints.add(content_fingerprint(body))
            except Exception:
                pass
    return slugs, titles, fingerprints


def html_to_text(html: str) -> str:
    """Convert HTML body to clean plain text."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
        tag.decompose()
    # Remove image captions and figcaptions that add noise
    for tag in soup(["figcaption"]):
        tag.decompose()

    text = soup.get_text(separator="\n\n")
    # Clean up whitespace
    lines = [line.strip() for line in text.split("\n")]
    # Collapse runs of empty lines into paragraph breaks
    cleaned = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                cleaned.append("")
            prev_empty = True
        else:
            cleaned.append(line)
            prev_empty = False
    return "\n\n".join(cleaned).strip()


def slugify(text: str) -> str:
    """Create a filesystem-safe slug from text."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:80]


def write_post(slug: str, title: str, date: str, content: str) -> Path:
    """Write a post file in the standard pipeline format."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Some old Squarespace slugs have date paths like "2016/10/18/post-name"
    safe_slug = slug.replace("/", "-")
    output_path = OUTPUT_DIR / f"{safe_slug}.txt"
    file_content = f"TITLE: {title}\nDATE: {date}\n\n{content}"
    output_path.write_text(file_content, encoding="utf-8")
    return output_path


# --- Squarespace ---


def scrape_squarespace(client: httpx.Client, dry_run: bool = False) -> list[dict]:
    """Scrape all blog posts from Squarespace JSON API."""
    known_slugs, known_titles, known_fps = existing_posts()
    posts = []
    skipped = 0
    errors = []
    offset = None
    page = 0

    print(f"Squarespace: fetching blog posts (dedup: {len(known_slugs)} slugs, {len(known_titles)} titles, {len(known_fps)} fingerprints)...")

    while True:
        page += 1
        url = f"{SQUARESPACE_BASE}/blog?format=json"
        if offset:
            url += f"&offset={offset}"

        try:
            resp = client.get(url)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            errors.append(f"Page {page}: {e}")
            break

        try:
            data = resp.json()
        except Exception:
            # Sometimes Squarespace returns HTML instead of JSON
            errors.append(f"Page {page}: non-JSON response")
            break

        items = data.get("items", [])
        if not items:
            break

        for item in items:
            slug = item.get("urlId", "")
            title = item.get("title", "").strip()
            body_html = item.get("body", "")
            publish_ms = item.get("publishOn", 0)

            if not slug or not title:
                continue

            # Convert publish timestamp (ms) to ISO date
            if publish_ms:
                dt = datetime.fromtimestamp(publish_ms / 1000, tz=timezone.utc)
                date_str = dt.strftime("%Y-%m-%d")
            else:
                date_str = ""

            content = html_to_text(body_html)
            word_count = len(content.split())

            if word_count < MIN_WORDS:
                continue

            # Dedup by slug, title, OR content fingerprint (existing files
            # used WordPress slugs, and Jacq retitles posts for SEO)
            fp = content_fingerprint(content)
            if slug in known_slugs or normalize_title(title) in known_titles or fp in known_fps:
                skipped += 1
                continue

            posts.append({
                "slug": slug,
                "title": title,
                "date": date_str,
                "content": content,
                "words": word_count,
            })

        # Pagination
        pagination = data.get("pagination", {})
        next_offset = pagination.get("nextPageOffset")
        if not next_offset or next_offset == offset:
            break
        offset = next_offset

        print(f"  Page {page}: {len(items)} posts (total new: {len(posts)})")
        time.sleep(RATE_LIMIT)

    print(f"  Found {len(posts)} new posts (skipped {skipped} existing)")

    if errors:
        print(f"  Errors: {len(errors)}")
        for e in errors:
            print(f"    - {e}")

    if not dry_run:
        for post in posts:
            path = write_post(post["slug"], post["title"], post["date"], post["content"])
            print(f"  Wrote: {path.name} ({post['words']} words)")

    return posts


# --- Substack ---


def discover_substack_posts(client: httpx.Client) -> list[dict]:
    """Discover Substack post URLs from the archive page and API."""
    posts = []

    # Substack has an API endpoint for listing posts
    api_url = f"{SUBSTACK_BASE}/api/v1/archive?sort=new&limit=100"
    try:
        resp = client.get(api_url)
        resp.raise_for_status()
        items = resp.json()
        for item in items:
            slug = item.get("slug", "")
            title = item.get("title", "").strip()
            post_date = item.get("post_date", "")
            if slug and title:
                date_str = ""
                if post_date:
                    try:
                        dt = datetime.fromisoformat(post_date.replace("Z", "+00:00"))
                        date_str = dt.strftime("%Y-%m-%d")
                    except ValueError:
                        pass
                posts.append({
                    "slug": f"substack-{slug}",
                    "title": title,
                    "date": date_str,
                    "url": f"{SUBSTACK_BASE}/p/{slug}",
                })
        if posts:
            return posts
    except httpx.HTTPError:
        pass

    # Fallback: scrape the archive page
    print("  Falling back to archive page scrape...")
    try:
        resp = client.get(f"{SUBSTACK_BASE}/archive")
        resp.raise_for_status()
    except httpx.HTTPError as e:
        print(f"  Failed to fetch archive: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/p/" in href and SUBSTACK_BASE in href:
            slug = href.rstrip("/").split("/p/")[-1].split("?")[0]
            title = link.get_text(strip=True) or slug.replace("-", " ").title()
            posts.append({
                "slug": f"substack-{slug}",
                "title": title,
                "date": "",
                "url": f"{SUBSTACK_BASE}/p/{slug}",
            })

    # Deduplicate by slug
    seen = set()
    unique = []
    for p in posts:
        if p["slug"] not in seen:
            seen.add(p["slug"])
            unique.append(p)

    return unique


def fetch_substack_post(client: httpx.Client, url: str) -> str:
    """Fetch and extract content from a single Substack post."""
    resp = client.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # Substack post body is in a div with class containing "post-content"
    body = (
        soup.find("div", class_="available-content")
        or soup.find("div", class_="post-content")
        or soup.find("div", class_="body")
    )
    if not body:
        # Try finding the main article content
        body = soup.find("article")
    if not body:
        return ""

    return html_to_text(str(body))


def scrape_substack(client: httpx.Client, dry_run: bool = False) -> list[dict]:
    """Scrape all posts from Substack."""
    known_slugs, known_titles, known_fps = existing_posts()
    errors = []

    print("Substack: discovering posts...")
    discovered = discover_substack_posts(client)
    print(f"  Found {len(discovered)} posts in archive")

    # Filter already-processed (by slug or title)
    new_posts = [
        p for p in discovered
        if p["slug"] not in known_slugs
        and normalize_title(p["title"]) not in known_titles
    ]
    print(f"  {len(new_posts)} are new (skipping {len(discovered) - len(new_posts)} existing)")

    if dry_run:
        for p in new_posts:
            print(f"  Would scrape: {p['title']}")
        return new_posts

    posts = []
    for p in new_posts:
        try:
            content = fetch_substack_post(client, p["url"])
            word_count = len(content.split())

            if word_count < MIN_WORDS:
                print(f"  Skipped (too short, {word_count} words): {p['title']}")
                continue

            fp = content_fingerprint(content)
            if fp in known_fps:
                print(f"  Skipped (duplicate content): {p['title']}")
                continue

            post = {**p, "content": content, "words": word_count}
            posts.append(post)
            path = write_post(post["slug"], post["title"], post["date"], post["content"])
            print(f"  Wrote: {path.name} ({word_count} words)")
        except httpx.HTTPError as e:
            errors.append(f"{p['title']}: {e}")
            print(f"  Error fetching: {p['title']} - {e}")

        time.sleep(RATE_LIMIT)

    if errors:
        print(f"  Errors: {len(errors)}")

    return posts


# --- Main ---


def main():
    parser = argparse.ArgumentParser(
        description="Scrape blog posts from Squarespace and Substack"
    )
    parser.add_argument(
        "--source",
        choices=["squarespace", "substack"],
        help="Scrape only this source (default: both)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be scraped without writing files",
    )
    args = parser.parse_args()

    client = make_client()
    total_new = 0

    try:
        if args.source in (None, "squarespace"):
            posts = scrape_squarespace(client, dry_run=args.dry_run)
            total_new += len(posts)

        if args.source in (None, "substack"):
            posts = scrape_substack(client, dry_run=args.dry_run)
            total_new += len(posts)
    finally:
        client.close()

    action = "Would scrape" if args.dry_run else "Scraped"
    print(f"\n{action} {total_new} new posts total")


if __name__ == "__main__":
    main()
