"""Extract blog posts from exported HTML/XML files.

Supports:
- WordPress XML export (most common)
- Directory of HTML files
- Directory of Markdown files

Place exports in data/raw/blog/ and run this script.
"""

import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup
from markdownify import markdownify


RAW_DIR = Path("data/raw/blog")
OUTPUT_DIR = Path("data/processed/blog")


def extract_wordpress_xml(xml_path: Path) -> list[dict]:
    """Extract posts from a WordPress XML export."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # WordPress namespaces
    namespaces = {
        "content": "http://purl.org/rss/1.0/modules/content/",
        "wp": "http://wordpress.org/export/1.2/",
        "dc": "http://purl.org/dc/elements/1.1/",
    }

    posts = []
    for item in root.iter("item"):
        post_type = item.find("wp:post_type", namespaces)
        status = item.find("wp:status", namespaces)

        # Only published posts (not pages, attachments, etc.)
        if post_type is not None and post_type.text != "post":
            continue
        if status is not None and status.text != "publish":
            continue

        title_el = item.find("title")
        content_el = item.find("content:encoded", namespaces)
        date_el = item.find("wp:post_date", namespaces)

        if title_el is None or content_el is None:
            continue

        title = title_el.text or ""
        content_html = content_el.text or ""
        date = date_el.text if date_el is not None else ""

        # Convert HTML to clean text
        soup = BeautifulSoup(content_html, "lxml")
        # Remove script/style tags
        for tag in soup(["script", "style"]):
            tag.decompose()
        content_text = soup.get_text(separator="\n\n")
        # Clean up excessive whitespace
        lines = [line.strip() for line in content_text.split("\n")]
        content_text = "\n\n".join(line for line in lines if line)

        if title.strip() and content_text.strip():
            posts.append({
                "title": title.strip(),
                "content": content_text.strip(),
                "date": date,
            })

    return posts


def extract_html_files(html_dir: Path) -> list[dict]:
    """Extract posts from individual HTML files."""
    posts = []
    for html_path in sorted(html_dir.glob("*.html")):
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "lxml")

        # Try to find the title
        title = ""
        title_tag = soup.find("h1") or soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()
        if not title:
            title = html_path.stem.replace("-", " ").replace("_", " ").title()

        # Get body content
        body = soup.find("article") or soup.find("main") or soup.find("body") or soup
        for tag in body(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        content = body.get_text(separator="\n\n")
        lines = [line.strip() for line in content.split("\n")]
        content = "\n\n".join(line for line in lines if line)

        if content.strip():
            posts.append({
                "title": title,
                "content": content.strip(),
                "date": "",
            })

    return posts


def extract_markdown_files(md_dir: Path) -> list[dict]:
    """Extract posts from individual Markdown files."""
    posts = []
    for md_path in sorted(md_dir.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")

        # Extract title from first H1 or filename
        lines = text.strip().split("\n")
        title = ""
        content_start = 0
        if lines and lines[0].startswith("# "):
            title = lines[0].lstrip("# ").strip()
            content_start = 1
        if not title:
            title = md_path.stem.replace("-", " ").replace("_", " ").title()

        content = "\n".join(lines[content_start:]).strip()
        if content:
            posts.append({
                "title": title,
                "content": content,
                "date": "",
            })

    return posts


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not RAW_DIR.exists():
        print(f"Directory {RAW_DIR}/ not found.")
        sys.exit(1)

    all_posts = []

    # Try WordPress XML exports
    for xml_path in RAW_DIR.glob("*.xml"):
        print(f"Extracting WordPress XML: {xml_path.name}")
        posts = extract_wordpress_xml(xml_path)
        print(f"  Found {len(posts)} published posts")
        all_posts.extend(posts)

    # Try HTML files
    html_files = list(RAW_DIR.glob("*.html"))
    if html_files:
        print(f"Extracting {len(html_files)} HTML files")
        posts = extract_html_files(RAW_DIR)
        all_posts.extend(posts)

    # Try Markdown files
    md_files = list(RAW_DIR.glob("*.md"))
    if md_files:
        print(f"Extracting {len(md_files)} Markdown files")
        posts = extract_markdown_files(RAW_DIR)
        all_posts.extend(posts)

    if not all_posts:
        print(f"No blog content found in {RAW_DIR}/")
        print("Supported formats:")
        print("  - WordPress XML export (*.xml)")
        print("  - HTML files (*.html)")
        print("  - Markdown files (*.md)")
        sys.exit(0)

    # Write each post as a separate file
    for i, post in enumerate(all_posts):
        # Create safe filename from title
        safe_title = "".join(
            c if c.isalnum() or c in " -_" else "" for c in post["title"]
        )
        safe_title = safe_title.strip().replace(" ", "-").lower()[:80]
        if not safe_title:
            safe_title = f"post-{i:04d}"

        output_path = OUTPUT_DIR / f"{safe_title}.txt"
        # Add title as first line for training data extraction
        content = f"TITLE: {post['title']}\n"
        if post["date"]:
            content += f"DATE: {post['date']}\n"
        content += f"\n{post['content']}"

        output_path.write_text(content, encoding="utf-8")

    print(f"\nDone. Extracted {len(all_posts)} blog posts to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
