"""Evaluate fine-tuned model outputs against Jacq's actual writing.

Metrics:
1. Style metrics: sentence length, vocabulary overlap, punctuation patterns
2. LLM-as-judge: use a larger model to rate style fidelity
3. Human-readable comparison output for manual review
"""

import json
import sys
from pathlib import Path

import httpx
from nltk.tokenize import sent_tokenize, word_tokenize
from rouge_score import rouge_scorer


OLLAMA_URL = "http://localhost:11434/api/generate"
TEST_DATA = Path("data/training/test.jsonl")
RESULTS_DIR = Path("data/evaluation")


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


def llm_judge(reference: str, generated: str, judge_model: str = "llama3.1:8b") -> dict:
    """Use an LLM to judge style fidelity."""
    judge_prompt = f"""Compare these two passages of writing. Passage A is the original by the author.
Passage B is AI-generated attempting to match the author's style.

Rate how well Passage B matches the author's style on a scale of 1-10 for each criterion:
1. Tone and emotional register
2. Sentence structure and rhythm
3. Vocabulary and word choice
4. Overall authenticity

Passage A (original):
{reference[:2000]}

Passage B (generated):
{generated[:2000]}

Respond with ONLY a JSON object like:
{{"tone": 7, "structure": 6, "vocabulary": 8, "authenticity": 7, "overall": 7, "notes": "brief comment"}}"""

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": judge_model,
                "prompt": judge_prompt,
                "stream": False,
                "options": {"temperature": 0.3},
            },
            timeout=120.0,
        )
        response.raise_for_status()
        text = response.json()["response"].strip()
        # Try to extract JSON from response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception as e:
        print(f"  Judge error: {e}")

    return {"error": "Failed to get judge response"}


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate fine-tuned model")
    parser.add_argument("--model", default="jacq:8b", help="Model to evaluate")
    parser.add_argument("--baseline", default="llama3.1:8b", help="Baseline model for comparison")
    parser.add_argument("--judge", default="llama3.1:8b", help="Model to use as judge")
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

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    ft_scores = [r["fine_tuned"]["judge"].get("overall", 0) for r in results if isinstance(r["fine_tuned"]["judge"].get("overall"), (int, float))]
    bl_scores = [r["baseline"]["judge"].get("overall", 0) for r in results if isinstance(r["baseline"]["judge"].get("overall"), (int, float))]

    if ft_scores:
        print(f"\nFine-tuned avg score: {sum(ft_scores)/len(ft_scores):.1f}/10")
    if bl_scores:
        print(f"Baseline avg score:   {sum(bl_scores)/len(bl_scores):.1f}/10")

    print(f"\nFull results saved to {output_path}")


if __name__ == "__main__":
    main()
