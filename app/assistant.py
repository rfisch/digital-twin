"""Core orchestration for the writing assistant.

Combines fine-tuned model + RAG retrieval to produce styled writing.
Manages Ollama lifecycle (start/stop on demand to conserve memory).
"""

import atexit
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from app.ollama_client import OllamaClient

# Load .env if present (no dependency — just reads KEY=VALUE lines)
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _key, _, _val = _line.partition("=")
            os.environ.setdefault(_key.strip(), _val.strip().strip("\"'"))

# Try to import RAG retriever (optional — works without it)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from rag.retriever import Retriever
    HAS_RAG = True
except ImportError:
    HAS_RAG = False

# Try to import Gemini researcher (optional — works without it)
try:
    from app.gemini_client import GeminiResearcher
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class OllamaManager:
    """Manage Ollama server lifecycle — start on demand, stop when done."""

    def __init__(self):
        self._process: subprocess.Popen | None = None
        self._started_by_us = False

    def ensure_running(self) -> bool:
        """Start Ollama if not already running. Returns True if ready."""
        try:
            httpx.get("http://localhost:11434", timeout=2.0)
            return True
        except httpx.ConnectError:
            pass

        ollama_bin = shutil.which("ollama")
        if not ollama_bin:
            print("Error: ollama not found. Install with: brew install ollama")
            return False

        print("Starting Ollama server...")
        self._process = subprocess.Popen(
            [ollama_bin, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={
                **dict(__import__("os").environ),
                "OLLAMA_FLASH_ATTENTION": "1",
                "OLLAMA_KV_CACHE_TYPE": "q8_0",
            },
        )
        self._started_by_us = True

        # Register cleanup
        atexit.register(self.stop)
        try:
            signal.signal(signal.SIGTERM, lambda *_: self.stop())
        except ValueError:
            pass  # Not main thread (e.g. FastAPI handler) — atexit is enough

        # Wait for server to be ready
        for _ in range(30):
            try:
                httpx.get("http://localhost:11434", timeout=2.0)
                print("Ollama server ready.")
                return True
            except httpx.ConnectError:
                time.sleep(0.5)

        print("Error: Ollama server failed to start.")
        return False

    def stop(self):
        """Stop Ollama if we started it."""
        if self._process and self._started_by_us:
            print("Stopping Ollama server...")
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
            self._started_by_us = False


class WritingAssistant:
    """Main writing assistant that combines fine-tuned model with RAG."""

    TASK_TYPES = ["blog", "email", "copywriting", "freeform", "email_reply", "linkedin"]

    def __init__(self, model: str = "jacq-v6:8b"):
        self.model = model
        self.ollama_mgr = OllamaManager()
        self.client = OllamaClient()
        self.retriever = Retriever() if HAS_RAG else None
        self._researcher: "GeminiResearcher | None" = None

    def _load_prompt_template(self, task_type: str) -> str:
        """Load a prompt template file."""
        template_path = PROMPTS_DIR / f"{task_type}.txt"
        if template_path.exists():
            return template_path.read_text(encoding="utf-8").strip()
        return "{topic}"

    def _load_system_prompt(self) -> str:
        """Load the system prompt."""
        path = PROMPTS_DIR / "system_prompt.txt"
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
        return "You are Jacq. Write in her distinctive voice."

    def _research_sender(self, sender_name: str, sender_email: str, email_body: str) -> str:
        """Research the sender via Gemini (lazy init). Returns context or empty."""
        if not HAS_GEMINI:
            return ""
        if self._researcher is None:
            self._researcher = GeminiResearcher()
        return self._researcher.research_sender(sender_name, sender_email, email_body)

    def _get_rag_context(self, query: str) -> str:
        """Retrieve relevant context from Jacq's writing corpus."""
        if not self.retriever:
            return ""
        try:
            results = self.retriever.retrieve(query, n_results=3)
            return self.retriever.format_context(results)
        except Exception:
            return ""

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Convert HTML body to clean plain text."""
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "figcaption"]):
            tag.decompose()
        text = soup.get_text(separator="\n\n")
        lines = [line.strip() for line in text.split("\n")]
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

    def _fetch_blog_post(self, url: str) -> dict:
        """Fetch a blog post from a URL. Returns {"title": str, "content": str}.

        Tries Squarespace JSON API first, falls back to HTML scraping.
        """
        # Try Squarespace JSON API
        try:
            resp = httpx.get(
                f"{url}?format=json",
                headers={"User-Agent": "Mozilla/5.0"},
                follow_redirects=True,
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()

            # Squarespace wraps single posts in "item"
            item = data.get("item", data)
            title = item.get("title", "").strip()
            body_html = item.get("body", "")

            if title and body_html:
                return {"title": title, "content": self._html_to_text(body_html)}
        except (httpx.HTTPError, json.JSONDecodeError, KeyError):
            pass

        # Fallback: scrape the HTML page directly
        resp = httpx.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            follow_redirects=True,
            timeout=15.0,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        title = ""
        title_tag = soup.find("h1") or soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Try common article containers
        body = (
            soup.find("article")
            or soup.find("div", class_="blog-item-content")
            or soup.find("div", class_="entry-content")
            or soup.find("main")
        )
        content = self._html_to_text(str(body)) if body else self._html_to_text(resp.text)

        return {"title": title, "content": content}

    @staticmethod
    def _clean_linkedin_output(text: str) -> str:
        """Strip title lines, preamble, and numbered lists from LinkedIn output."""
        import re

        lines = text.strip().split("\n")
        cleaned = []
        started = False

        for line in lines:
            stripped = line.strip()
            # Skip empty lines before content starts
            if not started and not stripped:
                continue
            # Skip title-like lines (all caps, or "Title: ...", or bold **Title**)
            if not started and (
                stripped.startswith("Title:") or
                stripped.startswith("**") and stripped.endswith("**") or
                stripped.startswith("Here's") or
                stripped.startswith("Here is")
            ):
                continue
            # Skip numbered list items — convert to prose
            if re.match(r"^\d+\.\s+\*\*.*\*\*$", stripped):
                continue
            if re.match(r"^\d+\.\s+\*\*", stripped):
                # Strip the number and bold markers
                stripped = re.sub(r"^\d+\.\s+\*\*([^*]+)\*\*:?\s*", r"\1: ", stripped)
                line = stripped

            started = True
            cleaned.append(line)

        return "\n".join(cleaned).strip()

    def generate(
        self,
        task_type: str,
        topic: str,
        use_rag: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        return_prompt: bool = False,
        **kwargs,
    ) -> str | tuple[str, dict]:
        """Generate writing in Jacq's voice.

        Args:
            task_type: One of 'blog', 'email', 'copywriting', 'freeform'
            topic: The main topic or request
            use_rag: Whether to include RAG context
            temperature: Generation temperature (higher = more creative)
            max_tokens: Maximum response length
            **kwargs: Additional template variables (recipient, purpose, etc.)
        """
        # Ensure Ollama is running
        if not self.ollama_mgr.ensure_running():
            return "Error: Could not start Ollama server."

        # Build the prompt
        system_prompt = self._load_system_prompt()

        if task_type == "email_reply":
            received_email = kwargs.get("received_email", topic)
            sender_name = kwargs.get("sender_name", "")
            sender_email = kwargs.get("sender_email", "")
            goal = kwargs.get("goal", "")
            tone_notes = kwargs.get("tone_notes", "")

            # Research sender via Gemini
            research = self._research_sender(sender_name, sender_email, received_email)
            if research and not research.startswith("[Research unavailable"):
                sender_context_block = (
                    f"Background on the sender ({sender_name}):\n{research}"
                )
            else:
                sender_context_block = ""

            template = self._load_prompt_template("email_reply")
            # Escape braces in pasted email to prevent .format() KeyError
            safe_email = received_email.replace("{", "{{").replace("}", "}}")
            user_prompt = template.format(
                received_email=safe_email,
                sender_context_block=sender_context_block,
                goal=goal or "reply appropriately",
                tone_notes=tone_notes or "match Jacq's natural tone",
            )
        elif task_type == "linkedin":
            post_data = self._fetch_blog_post(topic)
            template = self._load_prompt_template("linkedin")
            user_prompt = template.format(
                title=post_data["title"],
                content=post_data["content"],
            )
        elif task_type == "freeform":
            user_prompt = topic
        else:
            template = self._load_prompt_template(task_type)
            # Fill template variables
            user_prompt = template.format(
                topic=topic,
                context=kwargs.get("context", ""),
                email_type=kwargs.get("email_type", "professional"),
                recipient=kwargs.get("recipient", ""),
                purpose=kwargs.get("purpose", ""),
                key_points=kwargs.get("key_points", ""),
                medium=kwargs.get("medium", ""),
                audience=kwargs.get("audience", ""),
                message=kwargs.get("message", ""),
                tone=kwargs.get("tone", ""),
            )

        # Add RAG context if available
        rag_context = ""
        if use_rag:
            rag_context = self._get_rag_context(topic)

        if rag_context:
            full_prompt = f"{rag_context}\n\n---\n\n{user_prompt}"
        else:
            full_prompt = user_prompt

        # For LinkedIn, enforce constraints via system prompt + token cap
        if task_type == "linkedin":
            system_prompt += (
                "\n\nFORMAT OVERRIDE: You are writing a LinkedIn post. "
                "Output ONLY the post text — no title, no heading, no preamble like "
                "'Here\'s a sample' or 'Here\'s an example'. No numbered lists. "
                "No bullet points. Start with a punchy hook sentence. "
                "STRICT LIMIT: 150-300 words. Stop writing at 300 words."
            )
            # Cap tokens to ~400 (300 words ≈ 400 tokens) to force brevity
            max_tokens = min(max_tokens, 512)

        # Generate
        response = self.client.generate(
            prompt=full_prompt,
            model=self.model,
            system=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Post-process LinkedIn output: strip title/preamble if model added one
        if task_type == "linkedin":
            response = self._clean_linkedin_output(response)

        if return_prompt:
            return response, {"system": system_prompt, "user": full_prompt}
        return response

    def generate_linkedin_multi(
        self,
        url: str,
        count: int = 3,
        temperature: float = 0.6,
        max_tokens: int = 512,
    ) -> list[dict]:
        """Generate N LinkedIn posts from one blog URL, each with a distinct angle.

        Returns: [{"text": str, "prompt_info": dict}, ...]
        """
        if not self.ollama_mgr.ensure_running():
            return [{"text": "Error: Could not start Ollama server.", "prompt_info": {}}]

        post_data = self._fetch_blog_post(url)
        system_prompt = self._load_system_prompt()
        system_prompt += (
            "\n\nFORMAT OVERRIDE: You are writing a LinkedIn post. "
            "Output ONLY the post text — no title, no heading, no preamble like "
            "'Here\'s a sample' or 'Here\'s an example'. No numbered lists. "
            "No bullet points. Start with a punchy hook sentence. "
            "STRICT LIMIT: 150-300 words. Stop writing at 300 words."
        )

        results = []

        # Post 1: use standard linkedin.txt template
        template_1 = self._load_prompt_template("linkedin")
        user_prompt_1 = template_1.format(
            title=post_data["title"],
            content=post_data["content"],
        )

        response_1 = self.client.generate(
            prompt=user_prompt_1,
            model=self.model,
            system=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        response_1 = self._clean_linkedin_output(response_1)
        results.append({
            "text": response_1,
            "prompt_info": {"system": system_prompt, "user": user_prompt_1},
        })

        # Posts 2-N: use linkedin_multi.txt with prior posts as context
        if count > 1:
            template_multi = self._load_prompt_template("linkedin_multi")

        for i in range(1, count):
            prior_posts = "\n\n---\n\n".join(
                f"POST {j + 1}:\n{r['text']}" for j, r in enumerate(results)
            )
            user_prompt_n = template_multi.format(
                post_number=i,
                prior_posts=prior_posts,
                title=post_data["title"],
                content=post_data["content"],
            )

            response_n = self.client.generate(
                prompt=user_prompt_n,
                model=self.model,
                system=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            response_n = self._clean_linkedin_output(response_n)
            results.append({
                "text": response_n,
                "prompt_info": {"system": system_prompt, "user": user_prompt_n},
            })

        return results

    def shutdown(self):
        """Clean shutdown — stops Ollama if we started it."""
        self.ollama_mgr.stop()
