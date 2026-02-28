"""Analyze Jacq's writing style from processed text files.

Outputs statistics that inform the system prompt and training strategy:
- Sentence length distribution
- Vocabulary richness
- Common phrases and transitions
- Paragraph structure patterns
- Punctuation usage
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize


PROCESSED_DIR = Path("data/processed")


def ensure_nltk_data():
    """Download required NLTK data if not present."""
    for resource in ["punkt", "punkt_tab", "averaged_perceptron_tagger"]:
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)


def analyze_sentences(text: str) -> dict:
    """Analyze sentence-level patterns."""
    sentences = sent_tokenize(text)
    lengths = [len(word_tokenize(s)) for s in sentences]

    if not lengths:
        return {}

    return {
        "count": len(sentences),
        "avg_length_words": round(sum(lengths) / len(lengths), 1),
        "median_length_words": sorted(lengths)[len(lengths) // 2],
        "min_length_words": min(lengths),
        "max_length_words": max(lengths),
        "short_sentences_pct": round(
            sum(1 for l in lengths if l <= 8) / len(lengths) * 100, 1
        ),
        "long_sentences_pct": round(
            sum(1 for l in lengths if l >= 25) / len(lengths) * 100, 1
        ),
    }


def analyze_vocabulary(text: str) -> dict:
    """Analyze vocabulary patterns."""
    words = word_tokenize(text.lower())
    words = [w for w in words if w.isalpha()]

    if not words:
        return {}

    word_freq = Counter(words)
    unique_words = len(word_freq)

    return {
        "total_words": len(words),
        "unique_words": unique_words,
        "type_token_ratio": round(unique_words / len(words), 4),
        "top_50_words": word_freq.most_common(50),
        "hapax_legomena": sum(1 for w, c in word_freq.items() if c == 1),
    }


def analyze_paragraphs(text: str) -> dict:
    """Analyze paragraph structure."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    if not paragraphs:
        return {}

    lengths = [len(word_tokenize(p)) for p in paragraphs]
    sent_counts = [len(sent_tokenize(p)) for p in paragraphs]

    return {
        "count": len(paragraphs),
        "avg_length_words": round(sum(lengths) / len(lengths), 1),
        "avg_sentences_per_paragraph": round(
            sum(sent_counts) / len(sent_counts), 1
        ),
    }


def analyze_punctuation(text: str) -> dict:
    """Analyze punctuation usage patterns."""
    total_chars = len(text)
    if not total_chars:
        return {}

    patterns = {
        "exclamation_marks": text.count("!"),
        "question_marks": text.count("?"),
        "ellipses": text.count("..."),
        "dashes": text.count(" - "),
        "semicolons": text.count(";"),
        "colons": text.count(":"),
        "parentheses": text.count("("),
    }

    # Normalize per 1000 words
    word_count = len(text.split())
    if word_count > 0:
        patterns_per_1k = {
            f"{k}_per_1k_words": round(v / word_count * 1000, 1)
            for k, v in patterns.items()
        }
        patterns.update(patterns_per_1k)

    return patterns


def find_common_phrases(text: str, n: int = 3) -> list:
    """Find common n-grams (phrases)."""
    words = word_tokenize(text.lower())
    words = [w for w in words if w.isalpha() or w in ".,!?;:"]

    ngrams = []
    for i in range(len(words) - n + 1):
        gram = tuple(words[i : i + n])
        # Skip if ngram is all stopwords or punctuation
        if all(w in ".,!?;:" for w in gram):
            continue
        ngrams.append(gram)

    freq = Counter(ngrams)
    # Return phrases that appear at least 3 times
    common = [(list(gram), count) for gram, count in freq.most_common(50) if count >= 3]
    return common


def main():
    ensure_nltk_data()

    txt_files = list(PROCESSED_DIR.rglob("*.txt"))
    if not txt_files:
        print(f"No text files found in {PROCESSED_DIR}/")
        sys.exit(1)

    print(f"Analyzing {len(txt_files)} files from {PROCESSED_DIR}/\n")

    # Combine all text
    all_text = ""
    for txt_path in txt_files:
        all_text += txt_path.read_text(encoding="utf-8") + "\n\n"

    # Run analyses
    results = {
        "files_analyzed": len(txt_files),
        "total_characters": len(all_text),
        "sentences": analyze_sentences(all_text),
        "vocabulary": analyze_vocabulary(all_text),
        "paragraphs": analyze_paragraphs(all_text),
        "punctuation": analyze_punctuation(all_text),
        "common_phrases": find_common_phrases(all_text),
    }

    # Print summary
    print("=" * 60)
    print("STYLE ANALYSIS SUMMARY")
    print("=" * 60)

    s = results["sentences"]
    print(f"\nSentences:")
    print(f"  Total: {s.get('count', 0)}")
    print(f"  Avg length: {s.get('avg_length_words', 0)} words")
    print(f"  Short (≤8 words): {s.get('short_sentences_pct', 0)}%")
    print(f"  Long (≥25 words): {s.get('long_sentences_pct', 0)}%")

    v = results["vocabulary"]
    print(f"\nVocabulary:")
    print(f"  Total words: {v.get('total_words', 0):,}")
    print(f"  Unique words: {v.get('unique_words', 0):,}")
    print(f"  Type-token ratio: {v.get('type_token_ratio', 0)}")

    p = results["paragraphs"]
    print(f"\nParagraphs:")
    print(f"  Total: {p.get('count', 0)}")
    print(f"  Avg length: {p.get('avg_length_words', 0)} words")
    print(f"  Avg sentences per paragraph: {p.get('avg_sentences_per_paragraph', 0)}")

    punc = results["punctuation"]
    print(f"\nPunctuation (per 1k words):")
    for key in ["exclamation_marks_per_1k_words", "question_marks_per_1k_words",
                 "ellipses_per_1k_words", "dashes_per_1k_words"]:
        label = key.replace("_per_1k_words", "").replace("_", " ")
        print(f"  {label}: {punc.get(key, 0)}")

    phrases = results["common_phrases"][:20]
    print(f"\nTop recurring phrases:")
    for phrase, count in phrases:
        print(f"  \"{' '.join(phrase)}\" ({count}x)")

    # Save full results
    output_path = PROCESSED_DIR / "style_analysis.json"
    # Convert tuples to lists for JSON serialization
    results["vocabulary"]["top_50_words"] = [
        list(item) for item in results["vocabulary"].get("top_50_words", [])
    ]
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nFull results saved to {output_path}")
    print("\nUse these insights to refine prompts/system_prompt.txt")


if __name__ == "__main__":
    main()
