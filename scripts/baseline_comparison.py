#!/usr/bin/env python3
"""
Phase 3: Baseline Comparison — Base model vs Fine-tuned model

Runs both llama3.1:8b (with system prompt) and jacq:8b on identical prompts,
saves all outputs for side-by-side comparison.

Usage:
    python scripts/baseline_comparison.py
    python scripts/baseline_comparison.py --prompts-only  # just print prompts, don't run
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "evaluation" / "baseline"
SYSTEM_PROMPT_PATH = PROJECT_ROOT / "prompts" / "system_prompt.txt"

# --- Test prompts covering different writing tasks ---

TEST_PROMPTS = [
    # Blog posts — core use case
    {
        "id": "blog_morning",
        "category": "blog",
        "prompt": "Write a blog post about why morning routines matter for creative women.",
    },
    {
        "id": "blog_perfectionism",
        "category": "blog",
        "prompt": "Write a blog post about letting go of perfectionism in your writing.",
    },
    {
        "id": "blog_seasons",
        "category": "blog",
        "prompt": "Write a blog post about how the changing seasons can inspire your creative process.",
    },
    {
        "id": "blog_stuck",
        "category": "blog",
        "prompt": "Write a blog post about what to do when you feel completely stuck with your writing.",
    },
    {
        "id": "blog_boundaries",
        "category": "blog",
        "prompt": "Write a blog post about setting boundaries to protect your creative energy.",
    },
    # Emails — different tone
    {
        "id": "email_newsletter",
        "category": "email",
        "prompt": "Write a short weekly newsletter email to your subscribers about why handwriting still matters in a digital world.",
    },
    {
        "id": "email_invitation",
        "category": "email",
        "prompt": "Write an email inviting someone to be a guest on your podcast about how women write.",
    },
    # Copywriting — persuasive voice
    {
        "id": "copy_workshop",
        "category": "copy",
        "prompt": "Write a landing page description for a weekend writing retreat for women who want to finish their book.",
    },
    {
        "id": "copy_lead_magnet",
        "category": "copy",
        "prompt": "Write a short opt-in page for a free guide called '5 Ways to Find Your Writing Voice'.",
    },
    # Personal / reflective — deeper voice
    {
        "id": "personal_intuition",
        "category": "personal",
        "prompt": "Write a reflective piece about learning to trust your intuition as a writer.",
    },
    {
        "id": "personal_goodbye",
        "category": "personal",
        "prompt": "Write a short personal essay about a time you had to let go of something — a project, a dream, a chapter of your life — to make room for something new.",
    },
    # Advice / how-to — instructional voice
    {
        "id": "advice_blogging",
        "category": "advice",
        "prompt": "Write a post with 3 practical tips for women who want to start blogging but don't know where to begin.",
    },
]


def ensure_ollama_running() -> bool:
    """Start Ollama if not already running. Returns True if we started it."""
    result = subprocess.run(["pgrep", "-x", "ollama"], capture_output=True)
    if result.returncode == 0:
        return False
    print("Starting Ollama...")
    subprocess.Popen(["ollama", "serve"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    return True


def stop_ollama():
    """Stop Ollama."""
    subprocess.run(["pkill", "ollama"], capture_output=True)
    print("Ollama stopped.")


def generate(model: str, prompt: str, system: str = "") -> dict:
    """Call Ollama HTTP API and return the response with timing info."""
    import urllib.request

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 2048},
    }).encode()

    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
        elapsed = time.time() - start
        output = data.get("message", {}).get("content", "").strip()
        return {
            "model": model,
            "output": output,
            "elapsed_seconds": round(elapsed, 1),
            "error": None,
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "model": model,
            "output": "",
            "elapsed_seconds": round(elapsed, 1),
            "error": str(e),
        }


def run_comparison(prompts_only: bool = False):
    """Run all prompts through both models and save results."""
    system_prompt = SYSTEM_PROMPT_PATH.read_text().strip()

    if prompts_only:
        print(f"{'='*60}")
        print(f"  {len(TEST_PROMPTS)} test prompts")
        print(f"{'='*60}\n")
        for p in TEST_PROMPTS:
            print(f"[{p['id']}] ({p['category']})")
            print(f"  {p['prompt']}\n")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    we_started = ensure_ollama_running()

    # Verify both models are available
    list_result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    available = list_result.stdout
    for model in ["llama3.1:8b", "jacq:8b"]:
        if model not in available:
            print(f"ERROR: Model '{model}' not found in Ollama. Run: ollama pull {model}")
            sys.exit(1)

    results = []
    total = len(TEST_PROMPTS)

    for i, test in enumerate(TEST_PROMPTS, 1):
        prompt_id = test["id"]
        prompt_text = test["prompt"]
        category = test["category"]

        print(f"\n{'='*60}")
        print(f"  Prompt {i}/{total}: [{prompt_id}]")
        print(f"  {prompt_text}")
        print(f"{'='*60}")

        # --- Base model with system prompt ---
        print(f"\n  Running llama3.1:8b (with system prompt)...")
        base_result = generate("llama3.1:8b", prompt_text, system=system_prompt)
        print(f"  Done ({base_result['elapsed_seconds']}s, "
              f"{len(base_result['output'].split())} words)")

        # --- Fine-tuned model (system prompt baked in via training) ---
        print(f"  Running jacq:8b...")
        tuned_result = generate("jacq:8b", prompt_text)
        print(f"  Done ({tuned_result['elapsed_seconds']}s, "
              f"{len(tuned_result['output'].split())} words)")

        entry = {
            "id": prompt_id,
            "category": category,
            "prompt": prompt_text,
            "base_model": base_result,
            "fine_tuned": tuned_result,
        }
        results.append(entry)

        # Save individual files for easy reading
        prompt_dir = OUTPUT_DIR / prompt_id
        prompt_dir.mkdir(exist_ok=True)

        (prompt_dir / "prompt.txt").write_text(prompt_text)
        (prompt_dir / "base_llama3.1.txt").write_text(base_result["output"])
        (prompt_dir / "jacq_finetuned.txt").write_text(tuned_result["output"])

    # Save full results as JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = OUTPUT_DIR / f"comparison_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "system_prompt": system_prompt,
            "models": {
                "base": "llama3.1:8b",
                "fine_tuned": "jacq:8b",
            },
            "results": results,
        }, f, indent=2)

    # Generate summary report
    report_lines = [
        f"# Baseline Comparison Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"**Base model**: llama3.1:8b + system prompt",
        f"**Fine-tuned model**: jacq:8b (QLoRA, 600 iterations)",
        f"",
        f"---",
        f"",
    ]

    for entry in results:
        p = entry
        base = p["base_model"]
        tuned = p["fine_tuned"]
        base_words = len(base["output"].split())
        tuned_words = len(tuned["output"].split())

        report_lines.extend([
            f"## [{p['id']}] {p['category'].upper()}",
            f"**Prompt**: {p['prompt']}",
            f"",
            f"| | Base (llama3.1:8b) | Fine-tuned (jacq:8b) |",
            f"|---|---|---|",
            f"| Words | {base_words} | {tuned_words} |",
            f"| Time | {base['elapsed_seconds']}s | {tuned['elapsed_seconds']}s |",
            f"",
            f"### Base Model Output",
            f"",
            f"{base['output']}",
            f"",
            f"### Fine-Tuned Output",
            f"",
            f"{tuned['output']}",
            f"",
            f"---",
            f"",
        ])

    report_file = OUTPUT_DIR / "comparison_report.md"
    report_file.write_text("\n".join(report_lines))

    if we_started:
        stop_ollama()

    print(f"\n{'='*60}")
    print(f"  DONE — {total} prompts compared")
    print(f"{'='*60}")
    print(f"\n  Results JSON: {results_file}")
    print(f"  Report:       {report_file}")
    print(f"  Individual:   {OUTPUT_DIR}/<prompt_id>/")
    print(f"\n  Review the report to compare base vs fine-tuned outputs.")


def main():
    parser = argparse.ArgumentParser(
        description="Phase 3: Baseline comparison of base vs fine-tuned model")
    parser.add_argument("--prompts-only", action="store_true",
                        help="Just print the prompts, don't run models")
    args = parser.parse_args()
    run_comparison(prompts_only=args.prompts_only)


if __name__ == "__main__":
    main()
