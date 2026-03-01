"""Retrieve relevant context from ChromaDB for RAG-augmented generation."""

from pathlib import Path

import chromadb
import httpx


CHROMA_DIR = Path(__file__).resolve().parent / "chroma_db"
COLLECTION_NAME = "jacq_writing"

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"


class Retriever:
    """Retrieve relevant writing samples from Jacq's corpus."""

    def __init__(self, chroma_dir: str | Path = CHROMA_DIR, n_results: int = 5):
        self.client = chromadb.PersistentClient(path=str(chroma_dir))
        self.collection = self.client.get_collection(COLLECTION_NAME)
        self.n_results = n_results

    def _embed(self, text: str) -> list[float]:
        """Get embedding for a query."""
        response = httpx.post(
            OLLAMA_EMBED_URL,
            json={"model": EMBED_MODEL, "input": [text]},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()["embeddings"][0]

    def retrieve(self, query: str, n_results: int | None = None) -> list[dict]:
        """Retrieve the most relevant chunks for a query.

        Returns list of dicts with 'text', 'source', and 'distance' keys.
        """
        n = n_results or self.n_results
        embedding = self._embed(query)

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n,
        )

        retrieved = []
        for i in range(len(results["documents"][0])):
            retrieved.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source", "unknown"),
                "distance": results["distances"][0][i] if results["distances"] else None,
            })

        return retrieved

    def format_context(self, results: list[dict]) -> str:
        """Format retrieved results into a context string for the prompt."""
        if not results:
            return ""

        parts = ["Here are relevant excerpts from Jacq's previous writing:\n"]
        for i, r in enumerate(results, 1):
            parts.append(f"--- Excerpt {i} (from {r['source']}) ---")
            parts.append(r["text"])
            parts.append("")

        return "\n".join(parts)


def main():
    """Quick test of the retriever."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python rag/retriever.py 'your query here'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    retriever = Retriever()
    results = retriever.retrieve(query)

    print(f"Query: {query}\n")
    print(retriever.format_context(results))


if __name__ == "__main__":
    main()
