"""Evaluate fine-tuned model outputs against Jacq's actual writing.

Metrics:
1. Perplexity via MLX — how well each model predicts Jacq's held-out text
2. Embedding similarity — cosine sim to reference + corpus centroid via nomic-embed-text
3. Failure mode detection — Gemini checks for buzzwords, generic AI, specificity, directness
4. Style metrics — sentence length, vocabulary overlap, punctuation patterns, ROUGE
"""

import gc
import json
import math
import os
import re
import sys
import time
from pathlib import Path

import httpx
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from rouge_score import rouge_scorer


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
TEST_DATA = _PROJECT_ROOT / "data" / "training" / "test.jsonl"
RESULTS_DIR = _PROJECT_ROOT / "evaluation" / "metrics"
CHROMA_DIR = _PROJECT_ROOT / "rag" / "chroma_db"
COLLECTION_NAME = "jacq_writing"

# Adapter mapping: Ollama model name → (base MLX model, adapter path)
ADAPTER_MAP = {
    "jacq-v4:8b": ("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit", _PROJECT_ROOT / "adapters" / "jacq-v4"),
    "jacq-v5:8b": ("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit", _PROJECT_ROOT / "adapters" / "jacq-v5"),
    "jacq:8b": ("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit", _PROJECT_ROOT / "adapters" / "jacq-v4"),
}
BASELINE_MLX = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"


def load_test_examples(n: int = 20) -> list[dict]:
    """Load test examples for evaluation."""
    if not TEST_DATA.exists():
        print(f"{TEST_DATA} not found. Run split_dataset.py first.")
        sys.exit(1)

    examples = []
    with open(TEST_DATA, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples[:n]


def get_rag_context(query: str) -> str:
    """Retrieve relevant context from ChromaDB for RAG-augmented generation."""
    try:
        sys.path.insert(0, str(_PROJECT_ROOT))
        from rag.retriever import Retriever
        retriever = Retriever(n_results=3)
        results = retriever.retrieve(query)
        return retriever.format_context(results)
    except Exception as e:
        print(f"  RAG retrieval failed: {e}")
        return ""


def generate_response(model: str, prompt: str, system_prompt: str,
                      use_rag: bool = False) -> str:
    """Generate a response using Ollama, optionally with RAG context."""
    full_prompt = prompt
    if use_rag:
        rag_context = get_rag_context(prompt)
        if rag_context:
            full_prompt = f"{rag_context}\n\n---\n\n{prompt}"

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": full_prompt,
                "system": system_prompt,
                "stream": False,
                "options": {"temperature": 0.7},
            },
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"[ERROR: {e}]"


def compute_structural_metrics(text: str) -> dict:
    """Compute Jacq-specific structural metrics for a piece of text."""
    words = text.split()
    word_count = len(words)
    if word_count < 10:
        return {"dashes_per_1k": 0, "parens_per_1k": 0, "questions_per_1k": 0, "fragment_pct": 0}

    # Dashes per 1k words — count all dash-like punctuation used for asides
    # em-dash (—), en-dash (–), spaced hyphen ( - ), double hyphen (--)
    dash_count = (
        text.count("\u2014")    # — em dash
        + text.count("\u2013")  # – en dash
        + text.count(" - ")    # spaced hyphen (most common from Llama)
        + text.count(" -- ")   # double hyphen with spaces
    )
    dashes_per_1k = round((dash_count / word_count) * 1000, 2)

    # Parentheses per 1k words (should be low)
    paren_count = text.count("(")
    parens_per_1k = round((paren_count / word_count) * 1000, 2)

    # Question marks per 1k words
    question_count = text.count("?")
    questions_per_1k = round((question_count / word_count) * 1000, 2)

    # Fragment percentage (sentences under 5 words)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    total_sents = len(sentences)
    if total_sents > 0:
        fragments = sum(1 for s in sentences if len(s.split()) < 5)
        fragment_pct = round((fragments / total_sents) * 100, 1)
    else:
        fragment_pct = 0

    return {
        "dashes_per_1k": dashes_per_1k,
        "parens_per_1k": parens_per_1k,
        "questions_per_1k": questions_per_1k,
        "fragment_pct": fragment_pct,
    }


def compute_style_metrics(reference: str, generated: str) -> dict:
    """Compare style features between reference and generated text."""
    ref_sents = sent_tokenize(reference)
    gen_sents = sent_tokenize(generated)

    ref_lengths = [len(word_tokenize(s)) for s in ref_sents]
    gen_lengths = [len(word_tokenize(s)) for s in gen_sents]

    ref_words = set(word_tokenize(reference.lower()))
    gen_words = set(word_tokenize(generated.lower()))

    vocab_overlap = len(ref_words & gen_words) / len(ref_words | gen_words) if ref_words | gen_words else 0

    # Structural metrics for both reference and generated
    ref_structural = compute_structural_metrics(reference)
    gen_structural = compute_structural_metrics(generated)

    return {
        "ref_avg_sent_len": round(sum(ref_lengths) / len(ref_lengths), 1) if ref_lengths else 0,
        "gen_avg_sent_len": round(sum(gen_lengths) / len(gen_lengths), 1) if gen_lengths else 0,
        "vocab_overlap": round(vocab_overlap, 4),
        "ref_word_count": len(reference.split()),
        "gen_word_count": len(generated.split()),
        "ref_structural": ref_structural,
        "gen_structural": gen_structural,
    }


def compute_rouge(reference: str, generated: str) -> dict:
    """Compute ROUGE scores."""
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference, generated)
    return {
        "rouge1_f": round(scores["rouge1"].fmeasure, 4),
        "rouge2_f": round(scores["rouge2"].fmeasure, 4),
        "rougeL_f": round(scores["rougeL"].fmeasure, 4),
    }


# ── Embedding Similarity ──────────────────────────────────────────────────

def embed_text(text: str) -> list[float]:
    """Embed a single text via Ollama's nomic-embed-text.

    Truncates to ~2000 words to stay well within nomic-embed-text's 8192 token limit.
    """
    if not text or not text.strip():
        return [0.0] * 768  # nomic-embed-text dimension
    words = text.split()
    if len(words) > 2000:
        text = " ".join(words[:2000])
    response = httpx.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBED_MODEL, "input": [text]},
        timeout=60.0,
    )
    if response.status_code != 200:
        print(f"    Embed failed ({response.status_code}), text length: {len(words)} words")
        return [0.0] * 768
    return response.json()["embeddings"][0]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    dot = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    if norm == 0:
        return 0.0
    return float(dot / norm)


def compute_corpus_centroid() -> list[float]:
    """Compute the mean embedding of all ChromaDB documents (corpus centroid)."""
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(COLLECTION_NAME)
    all_embeddings = collection.get(include=["embeddings"])["embeddings"]
    centroid = np.mean(all_embeddings, axis=0)
    print(f"  Corpus centroid computed from {len(all_embeddings)} embeddings")
    return centroid.tolist()


def compute_embedding_similarity(reference: str, generated: str,
                                 centroid: list[float]) -> dict:
    """Compute embedding similarity to reference and corpus centroid."""
    ref_emb = embed_text(reference)
    gen_emb = embed_text(generated)
    return {
        "ref_similarity": round(cosine_similarity(gen_emb, ref_emb), 4),
        "centroid_similarity": round(cosine_similarity(gen_emb, centroid), 4),
    }


# ── Perplexity via MLX ────────────────────────────────────────────────────

def compute_perplexity_mlx(base_model: str, adapter_path: str | None = None) -> dict:
    """Compute perplexity on test.jsonl using MLX.

    Loads the model (with optional LoRA adapter), runs evaluation on the test
    set, and returns loss + perplexity. Frees model from memory after.
    """
    import mlx.core as mx
    from mlx_lm.utils import load
    from mlx_lm.tuner.datasets import ChatDataset, CacheDataset
    from mlx_lm.tuner.trainer import evaluate

    label = f"{base_model}" + (f" + {Path(adapter_path).name}" if adapter_path else "")
    print(f"  Loading {label}...")

    model, tokenizer = load(base_model, adapter_path=adapter_path)

    # Load test data as ChatDataset
    test_data = []
    with open(TEST_DATA, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                test_data.append(json.loads(line))

    dataset = CacheDataset(ChatDataset(test_data, tokenizer._tokenizer))

    print(f"  Evaluating on {len(dataset)} test examples...")
    loss = evaluate(
        model=model,
        dataset=dataset,
        batch_size=1,
        num_batches=-1,
        max_seq_length=2048,
    )

    perplexity = math.exp(loss)

    # Free memory
    del model, tokenizer, dataset
    gc.collect()
    mx.metal.clear_cache()

    result = {
        "loss": round(loss, 4),
        "perplexity": round(perplexity, 2),
        "num_examples": len(test_data),
    }
    print(f"  Loss: {result['loss']}, Perplexity: {result['perplexity']}")
    return result


# ── Failure Mode Detection (Gemini) ───────────────────────────────────────

FAILURE_MODE_PROMPT = """Analyze this text for writing quality issues. Answer these 4 questions with a JSON response.

TEXT:
{text}

1. BUZZWORD DETECTION: List any self-help or corporate buzzwords found (e.g. optimize, leverage, growth mindset, journey, dive in, unlock, empower, thrive, cultivate, manifest, intentional, mindset shift, level up, show up as, hold space). Return the list.

2. GENERIC AI DETECTION: Does this read like generic AI output? Look for: "In this article", "Let's dive in", numbered lists with no personality, hedging language ("it's important to note", "one might consider"), overly balanced paragraphs, lack of any specific opinion. Answer yes/no.

3. SPECIFICITY: Count concrete personal details — named people, real places, specific anecdotes, brand names, titles of books/movies/songs, dates, numbers. Return the count and list them.

4. CONVERSATIONAL DIRECTNESS: Rate 1-5 where 1=formal/academic and 5=brash/unfiltered (uses profanity, sentence fragments, starts sentences with And/But/So, talks directly to reader as "you"). Just the number.

Respond with ONLY a JSON object:
{{"buzzwords": ["word1", "word2"], "generic_ai": true/false, "specifics": {{"count": 3, "items": ["item1", "item2", "item3"]}}, "directness": 4}}"""


def gemini_failure_modes(text: str) -> dict:
    """Analyze a single text for failure modes using Gemini."""
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = FAILURE_MODE_PROMPT.format(text=text[:3000])

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"temperature": 0.1},
            )
            raw = response.text.strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(raw[start:end])
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s (attempt {attempt+1}/3)...")
                time.sleep(wait)
            else:
                print(f"  Gemini failure mode error: {e}")
                break

    return {"error": "Failed to get failure mode response"}


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate fine-tuned model")
    parser.add_argument("--model", default="jacq:8b", help="Model to evaluate")
    parser.add_argument("--baseline", default="llama3.1:8b", help="Baseline model for comparison")
    parser.add_argument("--n", type=int, default=10, help="Number of test examples")
    parser.add_argument("--rag", action="store_true", help="Enable RAG for fine-tuned model (off by default)")
    parser.add_argument("--skip-perplexity", action="store_true", help="Skip MLX perplexity (saves memory + time)")
    parser.add_argument("--skip-failure-modes", action="store_true", help="Skip Gemini failure mode analysis")
    args = parser.parse_args()

    use_rag = args.rag

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    examples = load_test_examples(args.n)
    print(f"Evaluating {len(examples)} test examples")
    print(f"  Fine-tuned model: {args.model}{' + RAG' if use_rag else ''}")
    print(f"  Baseline model: {args.baseline}")
    print(f"  Perplexity: {'skip' if args.skip_perplexity else 'MLX'}")
    print(f"  Failure modes: {'skip' if args.skip_failure_modes else 'Gemini'}")
    print()

    # ── Phase 1: Perplexity via MLX ───────────────────────────────────────
    perplexity_results = {}
    if not args.skip_perplexity:
        print("Phase 1: Computing perplexity via MLX")
        print("=" * 50)

        # Baseline (no adapter)
        print("\n[Baseline]")
        perplexity_results["baseline"] = compute_perplexity_mlx(BASELINE_MLX)

        # Fine-tuned (with adapter)
        adapter_info = ADAPTER_MAP.get(args.model)
        if adapter_info:
            base_model, adapter_path = adapter_info
            print(f"\n[Fine-tuned: {args.model}]")
            perplexity_results["fine_tuned"] = compute_perplexity_mlx(
                base_model, adapter_path=str(adapter_path)
            )
        else:
            print(f"\n  Warning: No adapter mapping for {args.model}, skipping fine-tuned perplexity")

        print()

    # ── Phase 2: Compute corpus centroid ──────────────────────────────────
    print("Phase 2: Computing corpus centroid from ChromaDB")
    print("=" * 50)
    centroid = compute_corpus_centroid()
    print()

    # ── Phase 3: Per-example generation + metrics ─────────────────────────
    print("Phase 3: Generating responses and computing metrics")
    print("=" * 50)

    results = []

    for i, example in enumerate(examples):
        messages = example["messages"]
        system_prompt = messages[0]["content"]
        user_prompt = messages[1]["content"]
        reference = messages[2]["content"]

        print(f"\n[{i+1}/{len(examples)}] {user_prompt[:80]}...")

        # Generate from both models (RAG only for fine-tuned)
        ft_response = generate_response(args.model, user_prompt, system_prompt,
                                        use_rag=use_rag)
        baseline_response = generate_response(args.baseline, user_prompt, system_prompt,
                                              use_rag=False)

        # Style + ROUGE
        ft_style = compute_style_metrics(reference, ft_response)
        baseline_style = compute_style_metrics(reference, baseline_response)
        ft_rouge = compute_rouge(reference, ft_response)
        baseline_rouge = compute_rouge(reference, baseline_response)

        # Embedding similarity
        ft_embedding = compute_embedding_similarity(reference, ft_response, centroid)
        baseline_embedding = compute_embedding_similarity(reference, baseline_response, centroid)

        print(f"  Embed sim (ref): FT {ft_embedding['ref_similarity']} | Base {baseline_embedding['ref_similarity']}")
        print(f"  Embed sim (corpus): FT {ft_embedding['centroid_similarity']} | Base {baseline_embedding['centroid_similarity']}")

        # Failure mode detection
        ft_failure = {}
        baseline_failure = {}
        if not args.skip_failure_modes:
            ft_failure = gemini_failure_modes(ft_response)
            baseline_failure = gemini_failure_modes(baseline_response)
            if "error" not in ft_failure:
                ft_bw = len(ft_failure.get("buzzwords", []))
                bl_bw = len(baseline_failure.get("buzzwords", []))
                ft_dir = ft_failure.get("directness", "?")
                bl_dir = baseline_failure.get("directness", "?")
                print(f"  Buzzwords: FT {ft_bw} | Base {bl_bw}")
                print(f"  Directness: FT {ft_dir}/5 | Base {bl_dir}/5")

        result = {
            "prompt": user_prompt,
            "reference": reference,
            "reference_preview": reference[:200],
            "fine_tuned": {
                "response": ft_response,
                "response_preview": ft_response[:200],
                "style_metrics": ft_style,
                "rouge": ft_rouge,
                "embedding": ft_embedding,
                "failure_modes": ft_failure,
            },
            "baseline": {
                "response": baseline_response,
                "response_preview": baseline_response[:200],
                "style_metrics": baseline_style,
                "rouge": baseline_rouge,
                "embedding": baseline_embedding,
                "failure_modes": baseline_failure,
            },
        }
        results.append(result)

    # ── Phase 4: Aggregate and save ───────────────────────────────────────
    print("\n")
    print("Phase 4: Aggregating results")
    print("=" * 50)

    from datetime import datetime
    ft_slug = args.model.replace(":", "-").replace("/", "-")
    bl_slug = args.baseline.replace(":", "-").replace("/", "-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_name = f"{ft_slug}_vs_{bl_slug}_{timestamp}"

    # Structured JSON output
    output_data = {
        "config": {
            "model": args.model,
            "baseline": args.baseline,
            "use_rag": use_rag,
            "n_examples": len(results),
            "skip_perplexity": args.skip_perplexity,
            "skip_failure_modes": args.skip_failure_modes,
        },
        "perplexity": perplexity_results,
        "examples": results,
    }

    output_path = RESULTS_DIR / f"{run_name}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    latest_path = RESULTS_DIR / "evaluation_results.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # ── Compute averages ──────────────────────────────────────────────────
    def avg(lst):
        return round(sum(lst) / len(lst), 2) if lst else 0

    ft_rouge1 = [r["fine_tuned"]["rouge"]["rouge1_f"] for r in results]
    bl_rouge1 = [r["baseline"]["rouge"]["rouge1_f"] for r in results]
    ft_vocab = [r["fine_tuned"]["style_metrics"]["vocab_overlap"] for r in results]
    bl_vocab = [r["baseline"]["style_metrics"]["vocab_overlap"] for r in results]
    ft_sent_len = [r["fine_tuned"]["style_metrics"]["gen_avg_sent_len"] for r in results]
    bl_sent_len = [r["baseline"]["style_metrics"]["gen_avg_sent_len"] for r in results]
    ref_sent_len = [r["fine_tuned"]["style_metrics"]["ref_avg_sent_len"] for r in results]

    ft_ref_sim = [r["fine_tuned"]["embedding"]["ref_similarity"] for r in results]
    bl_ref_sim = [r["baseline"]["embedding"]["ref_similarity"] for r in results]
    ft_centroid_sim = [r["fine_tuned"]["embedding"]["centroid_similarity"] for r in results]
    bl_centroid_sim = [r["baseline"]["embedding"]["centroid_similarity"] for r in results]

    ft_dashes = [r["fine_tuned"]["style_metrics"].get("gen_structural", {}).get("dashes_per_1k", 0) for r in results]
    bl_dashes = [r["baseline"]["style_metrics"].get("gen_structural", {}).get("dashes_per_1k", 0) for r in results]
    ft_frags = [r["fine_tuned"]["style_metrics"].get("gen_structural", {}).get("fragment_pct", 0) for r in results]
    bl_frags = [r["baseline"]["style_metrics"].get("gen_structural", {}).get("fragment_pct", 0) for r in results]

    # Failure mode averages
    ft_buzzword_counts = []
    bl_buzzword_counts = []
    ft_generic_count = 0
    bl_generic_count = 0
    ft_specificity = []
    bl_specificity = []
    ft_directness = []
    bl_directness = []

    if not args.skip_failure_modes:
        for r in results:
            ftf = r["fine_tuned"]["failure_modes"]
            blf = r["baseline"]["failure_modes"]
            if "error" not in ftf:
                ft_buzzword_counts.append(len(ftf.get("buzzwords", [])))
                ft_generic_count += 1 if ftf.get("generic_ai") else 0
                ft_specificity.append(ftf.get("specifics", {}).get("count", 0))
                ft_directness.append(ftf.get("directness", 0))
            if "error" not in blf:
                bl_buzzword_counts.append(len(blf.get("buzzwords", [])))
                bl_generic_count += 1 if blf.get("generic_ai") else 0
                bl_specificity.append(blf.get("specifics", {}).get("count", 0))
                bl_directness.append(blf.get("directness", 0))

    # ── Print summary ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    if perplexity_results:
        print("\nPerplexity (lower = better):")
        if "baseline" in perplexity_results:
            bl_ppl = perplexity_results["baseline"]
            print(f"  Baseline:   loss {bl_ppl['loss']}, perplexity {bl_ppl['perplexity']}")
        if "fine_tuned" in perplexity_results:
            ft_ppl = perplexity_results["fine_tuned"]
            print(f"  Fine-tuned: loss {ft_ppl['loss']}, perplexity {ft_ppl['perplexity']}")

    print(f"\nEmbedding similarity (higher = better):")
    print(f"  To reference:  FT {avg(ft_ref_sim)} | Base {avg(bl_ref_sim)}")
    print(f"  To corpus:     FT {avg(ft_centroid_sim)} | Base {avg(bl_centroid_sim)}")

    print(f"\nStructural metrics (fine-tuned / baseline):")
    print(f"  Dashes/1k:   {avg(ft_dashes)} / {avg(bl_dashes)}")
    print(f"  Fragment %:  {avg(ft_frags)} / {avg(bl_frags)}")
    print(f"  ROUGE-1:     {avg(ft_rouge1)} / {avg(bl_rouge1)}")

    if not args.skip_failure_modes and ft_buzzword_counts:
        print(f"\nFailure modes (fine-tuned / baseline):")
        print(f"  Avg buzzwords:   {avg(ft_buzzword_counts)} / {avg(bl_buzzword_counts)}")
        print(f"  Generic AI:      {ft_generic_count}/{len(ft_buzzword_counts)} / {bl_generic_count}/{len(bl_buzzword_counts)}")
        print(f"  Avg specificity: {avg(ft_specificity)} / {avg(bl_specificity)}")
        print(f"  Avg directness:  {avg(ft_directness)}/5 / {avg(bl_directness)}/5")

    print(f"\nFull results saved to {output_path}")

    # ── Write markdown report ─────────────────────────────────────────────
    def avg_structural(results, model_key, metric):
        vals = [r[model_key]["style_metrics"].get("gen_structural", {}).get(metric, 0) for r in results]
        return avg(vals)

    def avg_ref_structural(results, metric):
        vals = [r["fine_tuned"]["style_metrics"].get("ref_structural", {}).get(metric, 0) for r in results]
        return avg(vals)

    def better(ft_val, bl_val, lower_is_better=False):
        if lower_is_better:
            return "FT" if ft_val < bl_val else ("Base" if bl_val < ft_val else "Tie")
        return "FT" if ft_val > bl_val else ("Base" if bl_val > ft_val else "Tie")

    report_lines = [
        "# Evaluation Report",
        "",
        f"**Fine-tuned model**: {args.model}{' + RAG' if use_rag else ''}",
        f"**Baseline model**: {args.baseline}",
        f"**Test examples**: {len(results)}",
        "",
        "---",
        "",
    ]

    # Perplexity section
    if perplexity_results:
        report_lines.extend([
            "## Perplexity (MLX)",
            "",
            "Lower perplexity = model better predicts Jacq's writing patterns.",
            "",
            "| | Loss | Perplexity | Examples |",
            "|---|---|---|---|",
        ])
        if "baseline" in perplexity_results:
            bl_ppl = perplexity_results["baseline"]
            report_lines.append(f"| Baseline | {bl_ppl['loss']} | {bl_ppl['perplexity']} | {bl_ppl['num_examples']} |")
        if "fine_tuned" in perplexity_results:
            ft_ppl = perplexity_results["fine_tuned"]
            report_lines.append(f"| **Fine-tuned** | **{ft_ppl['loss']}** | **{ft_ppl['perplexity']}** | {ft_ppl['num_examples']} |")
        report_lines.extend(["", ""])

    # Embedding similarity section
    report_lines.extend([
        "## Embedding Similarity (nomic-embed-text)",
        "",
        "Cosine similarity — higher = text lives in the same semantic space as Jacq's writing.",
        "",
        "| Metric | Fine-tuned | Baseline | Better |",
        "|--------|-----------|----------|--------|",
        f"| Similarity to reference | {avg(ft_ref_sim)} | {avg(bl_ref_sim)} | {better(avg(ft_ref_sim), avg(bl_ref_sim))} |",
        f"| Similarity to corpus centroid | {avg(ft_centroid_sim)} | {avg(bl_centroid_sim)} | {better(avg(ft_centroid_sim), avg(bl_centroid_sim))} |",
        "",
    ])

    # Style metrics section
    report_lines.extend([
        "## Style Metrics",
        "",
        "| Metric | Reference (Jacq) | Fine-tuned | Baseline |",
        "|--------|-----------------|-----------|----------|",
        f"| Avg sentence length | {avg(ref_sent_len)} words | {avg(ft_sent_len)} words | {avg(bl_sent_len)} words |",
        f"| Vocabulary overlap | — | {avg(ft_vocab)} | {avg(bl_vocab)} |",
        f"| ROUGE-1 F1 | — | {avg(ft_rouge1)} | {avg(bl_rouge1)} |",
        "",
    ])

    # Structural metrics section
    report_lines.extend([
        "## Structural Metrics",
        "",
        "| Metric | Reference (Jacq) | Fine-tuned | Baseline |",
        "|--------|-----------------|-----------|----------|",
        f"| Dashes/1k words | {avg_ref_structural(results, 'dashes_per_1k')} | {avg_structural(results, 'fine_tuned', 'dashes_per_1k')} | {avg_structural(results, 'baseline', 'dashes_per_1k')} |",
        f"| Parentheses/1k words | {avg_ref_structural(results, 'parens_per_1k')} | {avg_structural(results, 'fine_tuned', 'parens_per_1k')} | {avg_structural(results, 'baseline', 'parens_per_1k')} |",
        f"| Questions/1k words | {avg_ref_structural(results, 'questions_per_1k')} | {avg_structural(results, 'fine_tuned', 'questions_per_1k')} | {avg_structural(results, 'baseline', 'questions_per_1k')} |",
        f"| Fragment % | {avg_ref_structural(results, 'fragment_pct')}% | {avg_structural(results, 'fine_tuned', 'fragment_pct')}% | {avg_structural(results, 'baseline', 'fragment_pct')}% |",
        "",
    ])

    # Failure mode section
    if not args.skip_failure_modes and ft_buzzword_counts:
        report_lines.extend([
            "## Failure Mode Analysis (Gemini)",
            "",
            "| Metric | Fine-tuned | Baseline | Better |",
            "|--------|-----------|----------|--------|",
            f"| Avg buzzwords | {avg(ft_buzzword_counts)} | {avg(bl_buzzword_counts)} | {better(avg(ft_buzzword_counts), avg(bl_buzzword_counts), lower_is_better=True)} |",
            f"| Flagged as generic AI | {ft_generic_count}/{len(ft_buzzword_counts)} | {bl_generic_count}/{len(bl_buzzword_counts)} | {better(ft_generic_count, bl_generic_count, lower_is_better=True)} |",
            f"| Avg specificity (count) | {avg(ft_specificity)} | {avg(bl_specificity)} | {better(avg(ft_specificity), avg(bl_specificity))} |",
            f"| Avg directness (1-5) | {avg(ft_directness)} | {avg(bl_directness)} | {better(avg(ft_directness), avg(bl_directness))} |",
            "",
        ])

    # Per-example results
    report_lines.extend([
        "## Per-Example Results",
        "",
    ])

    for i, r in enumerate(results, 1):
        ft = r["fine_tuned"]
        bl = r["baseline"]

        table_rows = [
            f"### Example {i}",
            f"**Prompt**: {r['prompt'][:120]}...",
            "",
            "| | Fine-tuned | Baseline |",
            "|---|---|---|",
            f"| ROUGE-1 | {ft['rouge']['rouge1_f']} | {bl['rouge']['rouge1_f']} |",
            f"| Vocab overlap | {ft['style_metrics']['vocab_overlap']} | {bl['style_metrics']['vocab_overlap']} |",
            f"| Word count | {ft['style_metrics']['gen_word_count']} | {bl['style_metrics']['gen_word_count']} |",
            f"| Embed sim (ref) | {ft['embedding']['ref_similarity']} | {bl['embedding']['ref_similarity']} |",
            f"| Embed sim (corpus) | {ft['embedding']['centroid_similarity']} | {bl['embedding']['centroid_similarity']} |",
        ]

        if not args.skip_failure_modes:
            ftf = ft.get("failure_modes", {})
            blf = bl.get("failure_modes", {})
            if "error" not in ftf and "error" not in blf:
                table_rows.extend([
                    f"| Buzzwords | {len(ftf.get('buzzwords', []))} | {len(blf.get('buzzwords', []))} |",
                    f"| Specificity | {ftf.get('specifics', {}).get('count', 0)} | {blf.get('specifics', {}).get('count', 0)} |",
                    f"| Directness | {ftf.get('directness', '?')}/5 | {blf.get('directness', '?')}/5 |",
                ])

        table_rows.append("")
        report_lines.extend(table_rows)

    report_path = RESULTS_DIR / f"{run_name}.md"
    report_path.write_text("\n".join(report_lines))

    latest_report = RESULTS_DIR / "evaluation_report.md"
    latest_report.write_text("\n".join(report_lines))

    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    main()
