"""Ingest Jacq's writing into ChromaDB for RAG retrieval.

Chunks all processed text, generates embeddings via Ollama's nomic-embed-text,
and stores them in a local ChromaDB collection.
"""

import sys
from pathlib import Path

import chromadb
import httpx
from tqdm import tqdm


PROCESSED_DIR = Path("data/processed")
CHROMA_DIR = Path("rag/chroma_db")
COLLECTION_NAME = "jacq_writing"

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks at sentence boundaries."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])

        # Try to end at a sentence boundary
        if end < len(words):
            for punct in [". ", "! ", "? ", ".\n"]:
                last_sent = chunk.rfind(punct)
                if last_sent > len(chunk) * 0.6:
                    chunk = chunk[: last_sent + 1]
                    end = start + len(chunk.split())
                    break

        chunks.append(chunk.strip())
        start = end - overlap

    return [c for c in chunks if len(c.split()) >= 20]


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings from Ollama."""
    response = httpx.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBED_MODEL, "input": texts},
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def main():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Delete existing collection if re-ingesting
    try:
        client.delete_collection(COLLECTION_NAME)
    except ValueError:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Gather all text files
    txt_files = list(PROCESSED_DIR.rglob("*.txt"))
    if not txt_files:
        print(f"No text files in {PROCESSED_DIR}/. Run extraction scripts first.")
        sys.exit(1)

    print(f"Ingesting {len(txt_files)} files into ChromaDB...")

    all_chunks = []
    all_metadatas = []
    all_ids = []

    for txt_path in txt_files:
        text = txt_path.read_text(encoding="utf-8")
        source = str(txt_path.relative_to(PROCESSED_DIR))
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{txt_path.stem}_{i:04d}"
            all_chunks.append(chunk)
            all_metadatas.append({"source": source, "chunk_index": i})
            all_ids.append(chunk_id)

    print(f"Generated {len(all_chunks)} chunks")

    # Embed and insert in batches
    batch_size = 32
    for i in tqdm(range(0, len(all_chunks), batch_size), desc="Embedding"):
        batch_chunks = all_chunks[i : i + batch_size]
        batch_metas = all_metadatas[i : i + batch_size]
        batch_ids = all_ids[i : i + batch_size]

        embeddings = get_embeddings(batch_chunks)
        collection.add(
            documents=batch_chunks,
            embeddings=embeddings,
            metadatas=batch_metas,
            ids=batch_ids,
        )

    print(f"\nDone. Stored {len(all_chunks)} chunks in {CHROMA_DIR}/")
    print(f"Collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    main()
