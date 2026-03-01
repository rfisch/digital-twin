"""Evaluate fine-tuned model outputs against Jacq's actual writing.

Metrics:
1. Style metrics: sentence length, vocabulary overlap, punctuation patterns
2. LLM-as-judge: use a larger model to rate style fidelity
3. Human-readable comparison output for manual review
"""

import json
import os
import sys
import time
from pathlib import Path

import httpx
from nltk.tokenize import sent_tokenize, word_tokenize
from rouge_score import rouge_scorer


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
OLLAMA_URL = "http://localhost:11434/api/generate"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
TEST_DATA = _PROJECT_ROOT / "data" / "training" / "test.jsonl"
RESULTS_DIR = _PROJECT_ROOT / "evaluation" / "metrics"


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


def generate_response(model: str, prompt: str, system_prompt: str) -> str:
    """Generate a response using Ollama."""
    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
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


def compute_style_metrics(reference: str, generated: str) -> dict:
    """Compare style features between reference and generated text."""
    ref_sents = sent_tokenize(reference)
    gen_sents = sent_tokenize(generated)

    ref_lengths = [len(word_tokenize(s)) for s in ref_sents]
    gen_lengths = [len(word_tokenize(s)) for s in gen_sents]

    ref_words = set(word_tokenize(reference.lower()))
    gen_words = set(word_tokenize(generated.lower()))

    vocab_overlap = len(ref_words & gen_words) / len(ref_words | gen_words) if ref_words | gen_words else 0

    return {
        "ref_avg_sent_len": round(sum(ref_lengths) / len(ref_lengths), 1) if ref_lengths else 0,
        "gen_avg_sent_len": round(sum(gen_lengths) / len(gen_lengths), 1) if gen_lengths else 0,
        "vocab_overlap": round(vocab_overlap, 4),
        "ref_word_count": len(reference.split()),
        "gen_word_count": len(generated.split()),
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


JUDGE_PROMPT_TEMPLATE = """You are an expert literary style analyst. Compare these two passages of writing.

Passage A is the ORIGINAL written by the author Jacqueline Fisch (Jacq). She is known for:
- Short, punchy sentences mixed with longer reflective ones (median 13 words)
- Conversational, direct tone — like talking to a friend
- Heavy use of rhetorical questions
- Frequent dashes for asides
- Starting paragraphs with "And", "But", "So"
- Occasional profanity for emphasis
- Personal anecdotes from her life (kids, chickens, yoga, writing coaching)
- Warm but no-nonsense encouragement
- Ending with a short, punchy call to reflection

Passage B is AI-generated, attempting to match Jacq's style.

Rate how well Passage B matches Jacq's SPECIFIC voice on a scale of 1-10 for each criterion:
1. Tone - Does it sound like Jacq talking to a friend, or generic AI writing?
2. Structure - Does it use her short punchy sentences, rhetorical questions, fragment style?
3. Vocabulary - Does it use her actual words and phrases, or generic blogger language?
4. Authenticity - Would someone who reads Jacq's blog believe she wrote this?

Passage A (Jacq's original):
{reference}

Passage B (AI-generated):
{generated}

Respond with ONLY a JSON object:
{{"tone": 7, "structure": 6, "vocabulary": 8, "authenticity": 7, "overall": 7, "notes": "brief comment"}}"""


def gemini_judge(reference: str, generated: str) -> dict:
    """Use Gemini as an external LLM judge with retry logic."""
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = JUDGE_PROMPT_TEMPLATE.format(
        reference=reference[:2000],
        generated=generated[:2000],
    )

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"temperature": 0.3},
            )
            text = response.text.strip()
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s (attempt {attempt+1}/3)...")
                time.sleep(wait)
            else:
                print(f"  Gemini judge error: {e}")
                break

    return {"error": "Failed to get Gemini judge response"}


def ollama_judge(reference: str, generated: str, judge_model: str = "llama3.1:8b") -> dict:
    """Use a local Ollama model as judge (fallback)."""
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        reference=reference[:2000],
        generated=generated[:2000],
    )

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": judge_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3},
            },
            timeout=120.0,
        )
        response.raise_for_status()
        text = response.json()["response"].strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception as e:
        print(f"  Ollama judge error: {e}")

    return {"error": "Failed to get judge response"}


def llm_judge(reference: str, generated: str, judge_model: str = "gemini") -> dict:
    """Route to the appropriate judge."""
    if judge_model == "gemini":
        return gemini_judge(reference, generated)
    return ollama_judge(reference, generated, judge_model)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate fine-tuned model")
    parser.add_argument("--model", default="jacq:8b", help="Model to evaluate")
    parser.add_argument("--baseline", default="llama3.1:8b", help="Baseline model for comparison")
    parser.add_argument("--judge", default="gemini", help="Judge model: 'gemini' for Gemini API, or an Ollama model name")
    parser.add_argument("--n", type=int, default=10, help="Number of test examples")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    examples = load_test_examples(args.n)
    print(f"Evaluating {len(examples)} test examples")
    print(f"  Fine-tuned model: {args.model}")
    print(f"  Baseline model: {args.baseline}")
    print(f"  Judge model: {args.judge}")
    print()

    results = []

    for i, example in enumerate(examples):
        messages = example["messages"]
        system_prompt = messages[0]["content"]
        user_prompt = messages[1]["content"]
        reference = messages[2]["content"]

        print(f"[{i+1}/{len(examples)}] {user_prompt[:80]}...")

        # Generate from both models
        ft_response = generate_response(args.model, user_prompt, system_prompt)
        baseline_response = generate_response(args.baseline, user_prompt, system_prompt)

        # Compute metrics
        ft_style = compute_style_metrics(reference, ft_response)
        baseline_style = compute_style_metrics(reference, baseline_response)

        ft_rouge = compute_rouge(reference, ft_response)
        baseline_rouge = compute_rouge(reference, baseline_response)

        # LLM judge
        ft_judge = llm_judge(reference, ft_response, args.judge)
        baseline_judge = llm_judge(reference, baseline_response, args.judge)

        result = {
            "prompt": user_prompt,
            "reference_preview": reference[:200],
            "fine_tuned": {
                "response_preview": ft_response[:200],
                "style_metrics": ft_style,
                "rouge": ft_rouge,
                "judge": ft_judge,
            },
            "baseline": {
                "response_preview": baseline_response[:200],
                "style_metrics": baseline_style,
                "rouge": baseline_rouge,
                "judge": baseline_judge,
            },
        }
        results.append(result)

        # Print comparison
        ft_score = ft_judge.get("overall", "?")
        bl_score = baseline_judge.get("overall", "?")
        print(f"  Fine-tuned: {ft_score}/10 | Baseline: {bl_score}/10")

    # Save results
    output_path = RESULTS_DIR / "evaluation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Compute averages
    ft_scores = [r["fine_tuned"]["judge"].get("overall", 0) for r in results if isinstance(r["fine_tuned"]["judge"].get("overall"), (int, float))]
    bl_scores = [r["baseline"]["judge"].get("overall", 0) for r in results if isinstance(r["baseline"]["judge"].get("overall"), (int, float))]

    def avg(lst):
        return round(sum(lst) / len(lst), 2) if lst else 0

    ft_rouge1 = [r["fine_tuned"]["rouge"]["rouge1_f"] for r in results]
    bl_rouge1 = [r["baseline"]["rouge"]["rouge1_f"] for r in results]
    ft_vocab = [r["fine_tuned"]["style_metrics"]["vocab_overlap"] for r in results]
    bl_vocab = [r["baseline"]["style_metrics"]["vocab_overlap"] for r in results]
    ft_sent_len = [r["fine_tuned"]["style_metrics"]["gen_avg_sent_len"] for r in results]
    bl_sent_len = [r["baseline"]["style_metrics"]["gen_avg_sent_len"] for r in results]
    ref_sent_len = [r["fine_tuned"]["style_metrics"]["ref_avg_sent_len"] for r in results]

    # Judge sub-scores
    judge_keys = ["tone", "structure", "vocabulary", "authenticity"]
    ft_sub = {k: avg([r["fine_tuned"]["judge"].get(k, 0) for r in results if isinstance(r["fine_tuned"]["judge"].get(k), (int, float))]) for k in judge_keys}
    bl_sub = {k: avg([r["baseline"]["judge"].get(k, 0) for r in results if isinstance(r["baseline"]["judge"].get(k), (int, float))]) for k in judge_keys}

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    if ft_scores:
        print(f"\nFine-tuned avg score: {avg(ft_scores)}/10")
    if bl_scores:
        print(f"Baseline avg score:   {avg(bl_scores)}/10")
    print(f"\nFull results saved to {output_path}")

    # Write markdown report
    report_lines = [
        "# Evaluation Report",
        f"",
        f"**Fine-tuned model**: {args.model}",
        f"**Baseline model**: {args.baseline}",
        f"**Judge model**: {args.judge}",
        f"**Test examples**: {len(results)}",
        f"",
        f"---",
        f"",
        f"## LLM-as-Judge Scores (1-10)",
        f"",
        f"| Criterion | Fine-tuned | Baseline | Delta |",
        f"|-----------|-----------|----------|-------|",
    ]
    for k in judge_keys:
        delta = ft_sub[k] - bl_sub[k]
        sign = "+" if delta > 0 else ""
        report_lines.append(f"| {k.title()} | {ft_sub[k]} | {bl_sub[k]} | {sign}{delta:.1f} |")
    ft_avg = avg(ft_scores)
    bl_avg = avg(bl_scores)
    delta = ft_avg - bl_avg
    sign = "+" if delta > 0 else ""
    report_lines.append(f"| **Overall** | **{ft_avg}** | **{bl_avg}** | **{sign}{delta:.1f}** |")

    report_lines.extend([
        f"",
        f"## Style Metrics",
        f"",
        f"| Metric | Reference (Jacq) | Fine-tuned | Baseline |",
        f"|--------|-----------------|-----------|----------|",
        f"| Avg sentence length | {avg(ref_sent_len)} words | {avg(ft_sent_len)} words | {avg(bl_sent_len)} words |",
        f"| Vocabulary overlap | — | {avg(ft_vocab)} | {avg(bl_vocab)} |",
        f"| ROUGE-1 F1 | — | {avg(ft_rouge1)} | {avg(bl_rouge1)} |",
        f"",
        f"## Per-Example Results",
        f"",
    ])

    for i, r in enumerate(results, 1):
        ft = r["fine_tuned"]
        bl = r["baseline"]
        ft_s = ft["judge"].get("overall", "?")
        bl_s = bl["judge"].get("overall", "?")
        notes = ft["judge"].get("notes", "")
        report_lines.extend([
            f"### Example {i}",
            f"**Prompt**: {r['prompt'][:120]}...",
            f"",
            f"| | Fine-tuned | Baseline |",
            f"|---|---|---|",
            f"| Judge score | {ft_s}/10 | {bl_s}/10 |",
            f"| ROUGE-1 | {ft['rouge']['rouge1_f']} | {bl['rouge']['rouge1_f']} |",
            f"| Vocab overlap | {ft['style_metrics']['vocab_overlap']} | {bl['style_metrics']['vocab_overlap']} |",
            f"| Word count | {ft['style_metrics']['gen_word_count']} | {bl['style_metrics']['gen_word_count']} |",
            f"",
        ])
        if notes:
            report_lines.append(f"Judge notes (fine-tuned): {notes}\n")

    report_path = RESULTS_DIR / "evaluation_report.md"
    report_path.write_text("\n".join(report_lines))
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    main()
