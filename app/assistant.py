"""Core orchestration for the writing assistant.

Combines fine-tuned model + RAG retrieval to produce styled writing.
Manages Ollama lifecycle (start/stop on demand to conserve memory).
"""

import atexit
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import httpx

from app.ollama_client import OllamaClient

# Try to import RAG retriever (optional — works without it)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from rag.retriever import Retriever
    HAS_RAG = True
except ImportError:
    HAS_RAG = False


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
        signal.signal(signal.SIGTERM, lambda *_: self.stop())

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

    TASK_TYPES = ["blog", "email", "copywriting", "freeform"]

    def __init__(self, model: str = "jacq:8b"):
        self.model = model
        self.ollama_mgr = OllamaManager()
        self.client = OllamaClient()
        self.retriever = Retriever() if HAS_RAG else None

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

    def _get_rag_context(self, query: str) -> str:
        """Retrieve relevant context from Jacq's writing corpus."""
        if not self.retriever:
            return ""
        try:
            results = self.retriever.retrieve(query, n_results=3)
            return self.retriever.format_context(results)
        except Exception:
            return ""

    def generate(
        self,
        task_type: str,
        topic: str,
        use_rag: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
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

        if task_type == "freeform":
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

        # Generate
        return self.client.generate(
            prompt=full_prompt,
            model=self.model,
            system=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def shutdown(self):
        """Clean shutdown — stops Ollama if we started it."""
        self.ollama_mgr.stop()
