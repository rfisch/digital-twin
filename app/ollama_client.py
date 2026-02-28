"""Ollama API client for model inference.

Supports both the fine-tuned jacq model and baseline models.
"""

import httpx


OLLAMA_URL = "http://localhost:11434"

DEFAULT_MODEL = "jacq:8b"
BASELINE_MODEL = "llama3.1:8b"


class OllamaClient:
    """Client for interacting with the Ollama API."""

    def __init__(self, base_url: str = OLLAMA_URL):
        self.base_url = base_url

    def generate(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> str | None:
        """Generate text from a model.

        Returns the full response text, or yields chunks if stream=True.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        if stream:
            return self._stream_generate(payload)

        response = httpx.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=180.0,
        )
        response.raise_for_status()
        return response.json()["response"]

    def _stream_generate(self, payload: dict):
        """Stream response tokens."""
        payload["stream"] = True
        with httpx.stream(
            "POST",
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=180.0,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]

    def chat(
        self,
        messages: list[dict],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Chat-style generation with message history."""
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
            timeout=180.0,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def list_models(self) -> list[str]:
        """List available models."""
        response = httpx.get(f"{self.base_url}/api/tags", timeout=10.0)
        response.raise_for_status()
        return [m["name"] for m in response.json().get("models", [])]

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            httpx.get(self.base_url, timeout=5.0)
            return True
        except httpx.ConnectError:
            return False
