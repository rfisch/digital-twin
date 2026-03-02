# ML/AI Concepts Reference

A beginner-friendly guide to every ML/AI concept used in this project. No prior machine learning experience required — we start from the basics and build up.

**How to use this guide:** Concepts are organized into a progressive learning path. Each part builds on the previous one. If you're brand new, read top-to-bottom. If you're looking up a specific term, use the table of contents.

## Table of Contents

### Part 1: Foundations — What Are We Working With?
1. [The Big Picture: How LLMs Work](#the-big-picture-how-llms-work)
2. [Weights and Parameters](#weights-and-parameters)
3. [Tokens and Tokenization](#tokens-and-tokenization)
4. [Transformers and Attention](#transformers-and-attention)

### Part 2: Using a Model — How Do We Talk To It?
5. [Inference](#inference)
6. [System Prompts](#system-prompts)
7. [Temperature and Sampling](#temperature-and-sampling)

### Part 3: Training a Model — How Do We Teach It Jacq's Voice?
8. [Pre-training — Where Base Models Come From](#pre-training--where-base-models-come-from)
9. [Fine-Tuning](#fine-tuning)
10. [LoRA (Low-Rank Adaptation)](#lora-low-rank-adaptation)
11. [Training Data Splits](#training-data-splits)
12. [Epochs and Batch Size](#epochs-and-batch-size)
13. [Learning Rate](#learning-rate)
14. [Loss (Training & Validation)](#loss-training-loss--validation-loss)
15. [Overfitting](#overfitting)
16. [Checkpoints](#checkpoints)
17. [Gradient Checkpointing](#gradient-checkpointing)

### Part 4: Evaluating the Model — How Do We Know It's Working?
18. [Perplexity](#perplexity)
19. [Embeddings and Similarity](#embeddings-and-similarity)
20. [MTEB Benchmark](#mteb-benchmark)
21. [LLM-as-Judge](#llm-as-judge)

### Part 5: Deployment — How Do We Ship and Serve It?
22. [Quantization and GGUF](#quantization-and-gguf)
23. [Safetensors](#safetensors)
24. [llama.cpp and Ollama](#llamacpp-and-ollama)

### Part 6: Advanced Patterns
25. [RAG (Retrieval-Augmented Generation)](#rag-retrieval-augmented-generation)

### Appendix
26. [Further Reading](#further-reading)

---

# Part 1: Foundations — What Are We Working With?

These concepts are the building blocks. Everything else in this guide depends on understanding these first.

---

## The Big Picture: How LLMs Work

Before diving into individual concepts, here's a 30-second mental model for how a Large Language Model (LLM) works:

```
┌─────────────────────────────────────────────────────┐
│                   HOW AN LLM GENERATES TEXT          │
│                                                      │
│   Input: "The cat sat on the ___"                    │
│                                                      │
│        ┌──────────────┐                              │
│        │  LLM Brain   │  Billions of numbers         │
│        │  (Weights)   │  learned from reading        │
│        │              │  the internet                │
│        └──────┬───────┘                              │
│               │                                      │
│               ▼                                      │
│   Probability of next word:                          │
│     "mat"    → 35%                                   │
│     "couch"  → 20%                                   │
│     "floor"  → 15%                                   │
│     "roof"   → 8%                                    │
│     ...thousands more options                        │
│               │                                      │
│               ▼                                      │
│   Pick one word → "mat"                              │
│   Now repeat for the NEXT word... and the next...    │
└─────────────────────────────────────────────────────┘
```

That's it. An LLM is a next-word prediction machine. Everything else in this guide — fine-tuning, temperature, LoRA — is about making that prediction machine better at a specific job.

> **Further reading:** [3Blue1Brown: Neural Networks](https://www.3blue1brown.com/topics/neural-networks) — an outstanding video series that visually explains how neural networks learn, starting from zero.

---

## Weights and Parameters

### What they are

A model's **weights** are the billions of numbers that encode everything it has learned. When we say a model has "8 billion parameters," we mean it contains 8 billion individual numbers, each one fine-tuned during training to help the model predict the next word.

### Analogy

Think of a piano. Each key can be pressed with different force (soft, medium, loud). A pianist's "style" is captured by how hard they press each key in each situation. The piano keys are the **parameters**; the specific pressure for each key is the **weight** (the learned value). Change the weights and you change the style.

```
A tiny model with 6 weights:

  Weight 1: 0.73    Weight 2: -0.12    Weight 3: 2.41
  Weight 4: 0.08    Weight 5: -1.67    Weight 6: 0.55

  Now imagine 8 BILLION of these.
  That's Llama 3.1 8B.

  Each one is a tiny dial that was adjusted during training
  to make the model better at predicting the next word.
```

### Why it matters

- **More parameters = more capacity** to learn complex patterns (but also more memory and compute needed)
- **Fine-tuning changes weights** — when we train on Jacq's writing, we're adjusting these numbers so the model predicts *her* next word better
- **LoRA only changes a small subset** of weights — that's why it's efficient (see [LoRA section](#lora-low-rank-adaptation))
- **Quantization reduces the precision** of each weight (e.g., from 16 bits to 4 bits) to save memory (see [Quantization section](#quantization-and-gguf))

> **Further reading:** [3Blue1Brown: What is a Neural Network?](https://www.3blue1brown.com/lessons/neural-networks) — visual explanation of how weights combine to make predictions.

---

## Tokens and Tokenization

### What it is

LLMs don't read words — they read **tokens**, which are chunks of text. Think of it like this: you read letter-by-letter as a toddler, then graduated to whole words. LLMs read in "token-sized" chunks somewhere in between.

### How tokenization breaks up text

```
Sentence: "Jacqueline writes amazing blog posts!"

Tokens:   ["Jac", "quel", "ine", " writes", " amazing", " blog", " posts", "!"]
             1       2       3        4           5         6        7       8

Compare:  "The cat sat"
Tokens:   ["The", " cat", " sat"]
             1       2       3
```

**Key insight:** Common words like "the" = 1 token. Unusual words like "Jacqueline" get split into multiple tokens. A rough rule of thumb: **1 token ~ 0.75 words** (or about 4 characters).

### Why it matters

| Parameter | Value | What it means |
|-----------|-------|---------------|
| `max_seq_length=2048` | Training | Max tokens per example. Longer blog posts get cut off. |
| `max_tokens=512` | LinkedIn | Caps output at ~350-400 words. Prevents endless generation. |
| `max_tokens=2048` | Blog posts | Allows longer-form content. |

The model's vocabulary is fixed (Llama 3.1 has ~128K possible tokens). It can only "think" in terms of these tokens.

> **Further reading:** [Hugging Face: Tokenizers](https://huggingface.co/learn/llm-course/en/chapter2/4) — interactive introduction to how tokenizers work and why they matter.

---

## Transformers and Attention

### What it is

A **transformer** is the specific type of neural network architecture that powers all modern LLMs (GPT, Llama, Claude, Gemini — all transformers). The key innovation: **attention**, which lets the model look at *all* the words in the input at once and figure out which ones matter for predicting the next word.

### Why attention matters — an example

```
"The cat sat on the mat because it was tired."

What does "it" refer to?
   → The cat? The mat?

ATTENTION lets the model connect "it" back to "cat"
by learning that, in this context, "it" and "cat"
are strongly related:

  The ─── cat ─── sat ─── on ─── the ─── mat ─── because ─── it
                                                              │
  Attention strength: ◄═══════════════ STRONG ════════════════╝
  (model learned "it" refers to "cat", not "mat")
```

Before transformers, models read text strictly left-to-right and struggled with long-range connections like this. Attention lets the model see the whole sentence at once.

### Why it matters for this project

- Llama 3.1 is a transformer. Every concept in this guide operates within the transformer architecture.
- The **system prompt** works because attention lets the model "look back" at those instructions while generating every single token.
- **LoRA adapters** are applied to the attention layers specifically — that's where the model's "style" lives.

> **Further reading:** [Jay Alammar: The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) — the best visual walkthrough of how transformers and attention work.

---

# Part 2: Using a Model — How Do We Talk To It?

Now that you understand what an LLM is made of, these concepts cover how you *use* one to generate text.

---

## Inference

### What it is

**Inference = using a trained model to generate text.** Training is school. Inference is the job.

```
TRAINING (learning phase)             INFERENCE (working phase)
┌────────────────────────┐           ┌────────────────────────┐
│  Feed model examples   │           │  User sends a prompt   │
│  of Jacq's writing     │           │         │              │
│         │              │           │         ▼              │
│         ▼              │           │  Model predicts one    │
│  Model adjusts its     │           │  token at a time       │
│  weights to match      │           │         │              │
│         │              │           │         ▼              │
│         ▼              │           │  "Write me a blog      │
│  Better at predicting  │           │   post about..."       │
│  Jacq's next word      │           │  → generates text      │
└────────────────────────┘           └────────────────────────┘
   Happens once (hours)                 Happens every time
                                        you use the model
                                        (~534 tokens/sec)
```

### In this project

- **MLX** handles training and evaluation (Apple Silicon native)
- **Ollama** handles inference/serving (loads the model, exposes an API)
- These are separate tools for separate jobs — MLX trains, Ollama serves
- Ollama runs on-demand (starts when needed, stops when done) to save memory

---

## System Prompts

### What it is

A special instruction given to the model *before* the user's message. It sets the model's identity, rules, and behavior — like a briefing document for an actor before they go on stage.

```
┌─────────────────────────────────────────────────────────────┐
│  SYSTEM PROMPT (the briefing)                               │
│  "You are Jacq. You write with em-dashes, sentence          │
│   fragments, rhetorical questions. You swear occasionally.  │
│   Never use: journey, authentic, intentional..."            │
├─────────────────────────────────────────────────────────────┤
│  USER MESSAGE (the task)                                    │
│  "Write a blog post about morning routines"                 │
├─────────────────────────────────────────────────────────────┤
│  MODEL RESPONSE (the output)                                │
│  "Look — I'm not going to pretend I'm a morning person..." │
└─────────────────────────────────────────────────────────────┘
```

### Critical rule: train = serve

The system prompt used during training **MUST** match the one used during generation. If you train with "use lots of dashes" but serve with "write formally," the model gets contradictory signals and the output suffers.

### Why this concept appears early in the guide

System prompts aren't an advanced topic — they're part of every single interaction with the model. You need to understand them *before* fine-tuning, because the system prompt is baked into every training example.

### Lessons from this project

- v5: Rewrote prompt with accurate statistics (dashes 7-14 per 1K words, 15% fragments) → immediate improvement
- v6: Replaced buzzy labels ("intentional living" → "doing things on purpose") → reduced buzzword output
- Wrong claims in the prompt (e.g., "use lots of metaphors" when Jacq doesn't) create contradictory training signals

---

## Temperature and Sampling

### Temperature — the creativity dial

A single number (0.0 to 1.0+) that controls how **creative vs. predictable** the model is.

```
Temperature = 0.0 (Robot Mode)        Temperature = 1.0 (Jazz Mode)
┌──────────────────────┐               ┌──────────────────────┐
│ ████████████  "mat"  │  95%          │ ████       "mat"     │  25%
│ █            "rug"   │   3%          │ ███        "couch"   │  20%
│              "couch" │   1%          │ ███        "rug"     │  18%
│              "floor" │   1%          │ ██         "floor"   │  15%
│                      │               │ ██         "roof"    │  12%
│ Always picks "mat"   │               │ █          "tree"    │  10%
│ Repetitive, safe     │               │ Could pick anything! │
└──────────────────────┘               │ Creative, surprising │
                                       └──────────────────────┘

    ◄────────────── Sweet Spot ──────────────►
    0.0    0.3    0.5    0.6    0.7    0.8    1.0
    │             │      │             │       │
    Robotic     Safe   Warm &       Creative  Wild &
              LinkedIn  natural     blog post unpredictable
```

**How it works technically:** Temperature divides the raw prediction scores (logits) before converting them to probabilities. Lower temperature = sharper distribution = the top choice dominates. Higher = flatter distribution = more options compete.

### Top-p (nucleus sampling) — temperature's partner

While temperature adjusts *how different* the probabilities are, **top-p** controls *how many* options the model considers.

```
Top-p = 0.9 means: "Only consider tokens whose combined
probability adds up to 90%. Ignore the long tail of
unlikely options."

All tokens ranked by probability:
  "mat"    35% ─┐
  "couch"  20% ─┤
  "floor"  15% ─┤── These add to 90%. Only pick from these.
  "rug"    12% ─┤
  "bed"     8% ─┘
  "tree"    3% ──── Ignored (in the 10% tail)
  "pizza"   1% ──── Ignored
  ...hundreds more tiny probabilities
```

Top-p and temperature work together. In this project we typically use **temperature 0.6-0.7** with **top-p 0.9** — a balanced combination that produces warm, natural writing without going off the rails.

### Top-k — the simpler alternative

**Top-k** just says "only consider the top K most likely tokens." Top-k=50 means: pick from the 50 most likely next words, ignore everything else. Simpler than top-p but less adaptive — it picks the same number of candidates regardless of whether the model is confident or uncertain.

### In this project

- **0.6 for LinkedIn posts** — warm enough for personality, controlled enough to stay on-topic
- **0.7 for blog posts** — slightly more creative latitude
- **0.3 was too cold** — voice sounded harsh and mechanical
- **0.8+ was too hot** — model started inventing facts and adding jargon

> **Further reading:** [Prompt Engineering Guide: LLM Settings](https://www.promptingguide.ai/introduction/settings) — clear explanation of temperature, top-p, and top-k alongside other generation parameters.

---

# Part 3: Training a Model — How Do We Teach It Jacq's Voice?

This is the heart of the project. These concepts cover how we take a generic language model and transform it into one that writes like Jacq.

---

## Pre-training — Where Base Models Come From

### What it is

Before we fine-tune a model on Jacq's writing, someone had to train it on *language in general*. That initial massive training run is called **pre-training**, and it's what makes the model "smart" in the first place.

```
PRE-TRAINING (done by Meta)              FINE-TUNING (done by us)
┌──────────────────────────┐            ┌──────────────────────────┐
│                          │            │                          │
│  Training data:          │            │  Training data:          │
│  Trillions of words      │            │  ~460 examples of        │
│  from the internet       │            │  Jacq's writing          │
│                          │            │                          │
│  Cost: Millions of $$$   │            │  Cost: Free              │
│  Time: Months on GPU     │            │  Time: ~1 hour on Mac    │
│        clusters          │            │        Studio            │
│                          │            │                          │
│  Result: A model that    │            │  Result: A model that    │
│  knows LANGUAGE           │            │  knows JACQ'S VOICE      │
│  (grammar, facts,        │            │  (her dashes, fragments, │
│   reasoning, style)      │            │   tone, vocabulary)      │
│                          │            │                          │
│  = Base Llama 3.1 8B     │            │  = jacq-v6:8b            │
└──────────────────────────┘            └──────────────────────────┘
```

### Why it matters

- We don't train from scratch — that would be impossibly expensive. We **stand on Meta's shoulders** by starting with Llama 3.1 8B, which already understands English, grammar, reasoning, and writing.
- Pre-training gives us a model that's already "instruction-tuned" — it knows how to follow system prompts and user requests. We just need to shift its *voice*.
- The base model's pre-training data influences fine-tuning. Llama 3.1 8B is naturally conversational and easy to steer — one reason we chose it over Qwen 2.5 14B, which resisted LoRA adaptation (v3 scored 2.5/10).

> **Further reading:** [Hugging Face: Supervised Fine-Tuning](https://huggingface.co/learn/llm-course/en/chapter11/1) — covers the full journey from pre-trained model to fine-tuned specialist.

---

## Fine-Tuning

### What it is

Taking a pre-trained model and training it further on specific data so it learns a particular style. The analogy: a fluent English speaker enrolling in a masterclass to write like Hemingway.

```
BEFORE Fine-Tuning                    AFTER Fine-Tuning
┌──────────────────────┐              ┌──────────────────────┐
│   Base Llama 3.1     │              │   Jacq's Model       │
│                      │              │                      │
│  "Here are 5 tips    │              │  "Look — I get it.   │
│   for productivity:  │              │   You're reading     │
│   1. Set clear       │              │   another damn       │
│      goals..."       │              │   productivity post  │
│                      │              │   and wondering why  │
│  Generic, helpful,   │              │   this one's gonna   │
│  sounds like every   │              │   be different."     │
│  AI assistant ever   │              │                      │
└──────────────────────┘              │  Dashes, fragments,  │
                                      │  rhetorical Qs,      │
                                      │  profanity, warmth   │
                                      └──────────────────────┘
```

### How it works

1. Start with a pre-trained model (Llama 3.1 8B — trained on trillions of words)
2. Feed it Jacq's actual writing in a structured format:
   - System prompt: "You are Jacq. Here are your style rules..."
   - User request: "Write about morning routines"
   - Target response: *Jacq's actual blog post about morning routines*
3. The model adjusts its weights to minimize the difference between what it *would* generate and what Jacq *actually* wrote
4. After training, its default voice shifts toward Jacq's patterns

### Types of fine-tuning

| Type | What it does | Used here? |
|------|-------------|-----------|
| Full fine-tuning | Retrain every parameter | No — too expensive |
| **LoRA fine-tuning** | Only train small adapter layers | **Yes — all versions** |
| Instruction tuning | Teach model to follow prompts | Already done by Meta |

### Key lessons from this project

- **Data quality > data quantity**: Removing podcast transcripts (v5) and filtering buzzword-heavy examples (v6) each improved output measurably
- **2 epochs is the sweet spot** for this dataset size (~460 examples on an 8B model)
- The system prompt used during training MUST match serving — mismatches create contradictory signals

---

## LoRA (Low-Rank Adaptation)

### What it is

A technique for fine-tuning that's like **adding a sticky note to a textbook instead of rewriting the whole book**. The original model (the textbook) stays frozen. LoRA adds small "adapter" layers that capture the new style.

### Why it's clever — the math, simplified

```
FULL FINE-TUNING                       LoRA FINE-TUNING
┌──────────────────────┐              ┌──────────────────────┐
│  Weight Matrix       │              │  Original Matrix     │
│  4096 x 4096         │              │  4096 x 4096         │
│  = 16 MILLION values │              │  (FROZEN - unchanged)│
│  to retrain          │              │         +            │
│                      │              │  Adapter A: 4096 x 16│
│  Expensive!          │              │  Adapter B: 16 x 4096│
│  Slow!               │              │  = 131K values       │
│  Needs huge GPU!     │              │                      │
│                      │              │  100x fewer params!  │
└──────────────────────┘              └──────────────────────┘
```

The "16" in the diagram is the **rank** — it controls adapter capacity. Think of it as: instead of updating a 4096x4096 grid of numbers, LoRA says "I can capture 99% of what changed using two skinny matrices that multiply together."

### Key parameters

| Parameter | Value | Plain English |
|-----------|-------|--------------|
| `lora_rank=16` | Adapter size | Higher = more capacity to learn, more overfitting risk. 16 is a good balance. |
| `lora_alpha=32` | Scaling factor | Controls how strongly adapters influence output. Typically 2x the rank. |
| Alpha / Rank = 2.0 | Learning rate multiplier | Standard range is 1.0-2.0. |

### Why LoRA is perfect for this project

- Train Llama 3.1 8B (8 billion parameters) on a Mac Studio in under an hour
- Uses ~7.8 GB memory instead of the 50+ GB a full fine-tune needs
- Adapter files are tiny (~50-100 MB) vs the full model (4.6 GB)
- Can keep multiple versions (v1-v6) without duplicating the base model
- Can always fall back to the base model if a version is bad

> **Further reading:** [Sebastian Raschka: Parameter-Efficient LLM Finetuning With LoRA](https://sebastianraschka.com/blog/2023/llm-finetuning-lora.html) — excellent, clearly-written deep dive with code examples.

---

## Training Data Splits

### What it is

Before training, you divide your data into separate groups with different jobs. This is how you prevent the model from "cheating" on its exam.

```
Jacq's full writing corpus: 573 examples
     │
     ├──► TRAINING SET (80%): ~458 examples
     │    The model learns from these.
     │    It sees them during training.
     │
     ├──► VALIDATION SET (10%): ~57 examples
     │    Used to check progress DURING training.
     │    The model never trains on these — they're
     │    the "practice exam" to detect overfitting.
     │
     └──► TEST SET (10%): ~58 examples
          Used to measure final quality AFTER training.
          The model never sees these until evaluation.
          This is the "real exam."
```

### Why you can't skip this

If you tested the model on data it trained on, it would score great — but only because it memorized the answers. The validation and test sets are the only honest measure of whether the model learned *patterns* (generalizable) vs. *specific text* (memorized).

### How each split is used in this project

| Split | When it's used | What it tells us |
|-------|---------------|-----------------|
| **Training** | During training (every iteration) | Training loss — is the model learning? |
| **Validation** | During training (every 100 steps) | Validation loss — is it *actually* learning or just memorizing? |
| **Test** | After training is complete | Perplexity, embedding similarity — final "grade" |

> **Further reading:** [Google ML Crash Course: Datasets and Generalization](https://developers.google.com/machine-learning/crash-course/overfitting) — interactive lessons on why data splitting matters.

---

## Epochs and Batch Size

### Epochs — how many times the model sees the data

One **epoch** = one complete pass through all training data.

```
Training Data: 458 examples of Jacq's writing

Epoch 1: See all 458 examples → Learn broad patterns
         "Oh, she uses a lot of dashes"

Epoch 2: See all 458 again → Refine and deepen
         "The dashes come after short punchy phrases, not randomly"

Epoch 3: See all 458 AGAIN → Diminishing returns
         "I've memorized her exact sentences now" ← BAD (overfitting)
```

**2 epochs is the sweet spot** for this project. Evidence:
- v1 (~0.87 epochs): Undertrained, didn't fully learn the voice
- v4 (2 epochs): Best generalization
- v2 (3 epochs): Over-smoothed — lost Jacq's edge and directness

### Batch size — how many examples per weight update

Think of it like studying:
- **Batch size = 1**: Read one essay, take notes, adjust understanding. Repeat.
- **Batch size = 32**: Read 32 essays, summarize your impressions, adjust understanding once.

Smaller batches use less memory but give "noisier" learning signals. All versions of this project use **batch_size=1** (due to memory constraints), which actually *helps* — the noise prevents the model from averaging out Jacq's stylistic quirks.

---

## Learning Rate

### What it is

The learning rate controls **how big of a step** the model takes when adjusting its weights after each training example. Too big and it overshoots; too small and it barely moves.

```
Adjusting weights to fit Jacq's voice:

Learning rate TOO HIGH        Learning rate JUST RIGHT      Learning rate TOO LOW

    ╱╲    ╱╲                       ╲                              ╲
   ╱  ╲  ╱  ╲  Overshooting!       ╲  ╱╲                          ╲
  ╱    ╲╱    ╲  Never settles.       ╲╱  ╲───── Converges          ╲
                                          smoothly.                  ╲────
                                                                Barely moves.
                                                                Takes forever.
```

### How it connects to LoRA

In this project, the effective learning rate for the LoRA adapters is controlled by the **alpha/rank ratio**:

- `lora_alpha=32` / `lora_rank=16` = **2.0** — a standard multiplier
- This means the adapter updates are scaled by 2x before being applied
- A ratio of 1.0-2.0 is the standard range for LoRA fine-tuning
- The actual base learning rate is set in the training config (typically 1e-5 to 1e-4 for LoRA)

You generally don't need to tune the learning rate much with LoRA — the alpha/rank ratio handles the scaling, and the defaults work well for most voice-cloning tasks.

---

## Loss (Training Loss & Validation Loss)

### What it is

A number that measures **how wrong the model's predictions are**. Lower = better. Training is the process of making this number go down.

### How it works

```
Model reads: "The cat sat on the ___"
Actual next word: "mat"

Model predicts:
  "mat"   → 10% confidence    ← Not very sure about the right answer
  "floor" → 30% confidence    ← More confident about a wrong answer!
  "the"   → 15% confidence

Loss = HIGH (model was wrong/uncertain)

After more training...

Model predicts:
  "mat"   → 75% confidence    ← Much better!
  "floor" → 8% confidence
  "the"   → 3% confidence

Loss = LOW (model is getting it right)
```

### The two types of loss — and why both matter

```
  Loss
  ▲
  │
3 ┤ T╲
  │   T╲  V        V                    KEY
  │    T╲V╱─V        V                  ─── T = Training loss
  │     VT    ╲V       V────V────V       ─── V = Validation loss
  │      ╲T     ╲V
  │       ╲T─────T                       Training loss ALWAYS drops.
  │              T───T───T───T───T       Validation loss drops, then RISES.
1 ┤                                      The split = overfitting.
  │
  └──┬─────┬─────┬─────┬─────┬───► Training iterations
    100   200   300   400   500
                 ▲           ▲
                 │           │
           Best checkpoint   Overfitting zone
           (lowest V loss)   (V rising, T still dropping)
```

**Reading the chart:** Both lines start high and drop together (the model is learning). At some point, the V (validation) line **bottoms out and starts climbing back up** while the T (training) line keeps falling. That split is where the model stops learning general patterns and starts memorizing specific training examples.

- **Training loss**: Measured on data the model trains on. Always goes down — the model gets better at data it's seen.
- **Validation loss**: Measured on held-out data the model *never* sees during training. This is the real measure of learning.
- **The gap** between them tells you about overfitting (see next section).

### Key values in this project

| Version | Val Loss | Train-Val Gap | Interpretation |
|---------|----------|---------------|----------------|
| v1 | 2.086 | — | Undertrained, short run |
| v4 | 1.507 | 0.047 | Best generalization |
| v6 | 1.138 | 0.083 | Best overall, mild overfitting onset |

> **Further reading:** [Google ML Crash Course: Interpreting Loss Curves](https://developers.google.com/machine-learning/crash-course/overfitting/interpreting-loss-curves) — interactive visualizations showing how to read training vs. validation loss curves.

---

## Overfitting

### What it is

When a model **memorizes** the training data instead of **learning** the patterns. Like a student who memorizes essay answers word-for-word instead of understanding the material — they ace the practice test but bomb the real exam.

### Visual intuition

```
HEALTHY MODEL (generalizing)          OVERFIT MODEL (memorizing)
┌──────────────────────┐              ┌──────────────────────┐
│                      │              │                      │
│  Training data ●●●   │              │  Training data ●●●   │
│               ●  ●   │              │        ●  ●          │
│  Learns the ─── ──── │              │  Memorizes ╭╮╭─╮    │
│  general    smooth   │              │  every    ╯  ╰╯  ╰── │
│  trend      curve    │              │  wiggle              │
│              ●●●     │              │    ●●●               │
│                      │              │                      │
│  New data? Works!    │              │  New data? Fails!    │
└──────────────────────┘              └──────────────────────┘
```

### How to spot it

Watch the gap between training loss and validation loss:

| Train Loss | Val Loss | Gap | Diagnosis |
|-----------|---------|-----|-----------|
| 1.30 | 1.24 | 0.06 | Healthy — generalizing well |
| 1.30 | 1.45 | 0.15 | Mild concern — keep watching |
| 1.10 | 1.80 | 0.70 | Overfitting — memorizing, not learning |

### Why it matters for this project

An overfit Jacq model would **parrot back exact training phrases** instead of writing *new* content in her voice. This is what happened with v2 (3 epochs) — the voice got "over-smoothed" and lost Jacq's edge and directness.

**Mitigation:** Checkpoints saved every 100 steps let us pick the best iteration *before* overfitting kicked in. v6's best was iteration 600 out of 916 — the final checkpoint was already starting to overfit.

---

## Checkpoints

### What it is

Snapshots of the model's weights saved at regular intervals during training. Like **save points in a video game** — you can go back to any point if things go wrong later.

```
Training timeline:
iter 100  iter 200  iter 300  iter 400  iter 500  iter 600  iter 700  iter 800  iter 916
  [save]    [save]    [save]    [save]    [save]   [BEST]    [save]    [save]    [save]
                                                     │
                                              Best checkpoint!
                                              (lowest val loss)

    ◄──── Model improving ────►◄──── Overfitting starts ────►
```

### Why this matters

**The best checkpoint is often NOT the final one.** v6's best was iteration 600 out of 916 total. After 600, validation loss started rising (overfitting onset) — later checkpoints are actually *worse*.

Without checkpoints, you'd be stuck with the final (potentially overfit) model. Checkpoint files are named by iteration: `0000600_adapters.safetensors`.

---

## Gradient Checkpointing

### What it is

A memory-saving training technique. During training, the model computes intermediate values at every layer. Normally these are all kept in memory for the backward pass (updating weights). **Gradient checkpointing discards most of them and recomputes as needed.**

### The tradeoff

```
                          Memory         Speed
                          ──────         ─────
Without grad checkpoint:  ~62 GB         Faster      ← Would crash our machine
With grad checkpoint:     ~6-8 GB        ~2x slower  ← Fits easily in 96 GB
```

This is what makes training Llama 3.1 8B with LoRA *possible* on consumer hardware. Without it, the 96 GB Mac Studio wouldn't have enough memory.

Enabled via `grad_checkpoint: true` in `configs/lora_config.yaml`.

---

# Part 4: Evaluating the Model — How Do We Know It's Working?

Training a model is only half the battle. These concepts cover how we *measure* whether the model actually sounds like Jacq.

---

## Perplexity

### What it is

Measures how **"surprised"** the model is by text it hasn't seen. Lower perplexity = the model better "gets" the writing patterns.

### Intuition

```
Perplexity = how many words the model is choosing between on average

Perplexity 3.3                         Perplexity 8.2
┌──────────────────────┐               ┌──────────────────────┐
│                      │               │                      │
│  Next word is...     │               │  Next word is...     │
│                      │               │                      │
│  Option A  ████████  │               │  Option A  ███       │
│  Option B  ████      │               │  Option B  ███       │
│  Option C  ██        │               │  Option C  ██        │
│                      │               │  Option D  ██        │
│  Only ~3 real        │               │  Option E  ██        │
│  contenders          │               │  Option F  █         │
│                      │               │  Option G  █         │
│  Model is CONFIDENT  │               │  Option H  █         │
│  (knows the style!)  │               │                      │
│                      │               │  Model is UNCERTAIN  │
└──────────────────────┘               │  (doesn't know the   │
                                       │   style well)        │
                                       └──────────────────────┘
```

### The math (simple version)

Perplexity = e^(loss). So:
- Loss 1.138 → Perplexity ~3.1 (fine-tuned v6 — confident)
- Loss 2.086 → Perplexity ~8.1 (v1 — much less sure)

### Why it matters

Perplexity directly measures whether fine-tuning helped the model internalize Jacq's language patterns — no judge, no subjective style description needed. Just: "Does the model predict her words better than baseline?"

> **Further reading:** [Two Minutes NLP: Perplexity Explained with Simple Probabilities](https://medium.com/nlplanet/two-minutes-nlp-perplexity-explained-with-simple-probabilities-6cdc46884584) — quick, intuitive walkthrough of the concept.

---

## Embeddings and Similarity

### What it is

A way to convert text into **numbers** so a computer can measure how "similar" two pieces of writing are.

### How it works

An embedding model reads text and outputs a vector (a list of numbers). These numbers capture meaning, style, and tone. Texts with similar meaning end up as vectors pointing in similar directions.

```
Imagine a 2D map of writing styles (real embeddings have 768+ dimensions):

   Formal ▲
          │        ● Academic paper
          │
          │  ● News article
          │
          │                    ● Corporate blog
          │
          │        ● Jacq's writing ←── We want generated
          │        ● Generated text         text to land HERE
          │
          │  ● Casual tweet
          │
          └──────────────────────────────► Creative

   Cosine similarity between Jacq's writing and generated text:
   1.0 = identical direction (perfect match)
   0.0 = completely unrelated (perpendicular)
```

### Cosine similarity — the comparison tool

Instead of measuring distance (which depends on text length), cosine similarity measures the **angle** between two vectors. Two texts pointing in the same direction are similar regardless of how long they are.

### In this project

- Uses **nomic-embed-text** (runs in Ollama) to create embeddings
- v6 embedding similarity: **0.75** (up from v5's 0.70) — measurable improvement
- RAG was shown to *hurt* similarity (0.70 → 0.67) — retrieved chunks made output *less* like Jacq
- This is one of three core evaluation metrics in `scripts/evaluate.py`

> **Further reading:** [Jay Alammar: The Illustrated Word2vec](https://jalammar.github.io/illustrated-word2vec/) — the gold standard for visual explanations of embeddings and vector similarity.

### Our embedding model: nomic-embed-text v1.5

We use **nomic-embed-text v1.5** by [Nomic AI](https://www.nomic.ai/) for all embedding tasks. Here's why — and whether we should reconsider.

```
┌─────────────────────────────────────────────────────────┐
│  nomic-embed-text v1.5  — Profile                       │
├──────────────────┬──────────────────────────────────────┤
│  Parameters      │  137M (very small)                   │
│  Dimensions      │  768 (supports 64-768 via Matryoshka)│
│  Context window  │  8,192 tokens (~6K words)            │
│  Model size      │  ~274 MB in Ollama                   │
│  MTEB score      │  ~62.4 (benchmark average)           │
│  License         │  Fully open source + open data       │
└──────────────────┴──────────────────────────────────────┘
```

**What it's used for in this project:**

| Use case | How | Why embeddings matter |
|----------|-----|----------------------|
| **Style similarity eval** | Generate text → embed it → compare to Jacq's real writing | Measures if output "sounds like" Jacq |
| **ChromaDB vector store** | Embed Jacq's blog posts → store in ChromaDB → retrieve by similarity | Powers RAG retrieval (when enabled) |

**Why we chose it:**
- **Runs 100% locally** — no API calls, no cloud, no per-token costs. Privacy-first.
- **Tiny memory footprint** — 274 MB leaves plenty of room for the 4.6 GB generation model
- **Long context** — 8K tokens means we can embed full blog posts without truncation
- **Fast** — 137M params means near-instant embedding generation on M3 Ultra
- **Good enough** — at launch it matched OpenAI's text-embedding-3-small (MTEB ~62.3)

**Known weaknesses:**
- **Outscored by larger models** — models in the 335M param class (mxbai, bge, gte) beat it by 2-3 MTEB points
- **768 max dimensions** — competitors offer 1024, capturing more stylistic nuance
- **Aging** — released early 2024, the embedding landscape has moved fast since then

### Should we switch? Alternatives compared

```
Quality vs. Size tradeoff:

MTEB Score
(higher = better embeddings)

  71 ┤                                          ★ Qwen3-Embedding-8B
     │                                            (4.7 GB, 32K context)
  67 ┤                              ★ e5-mistral-7b
     │                                (4.1 GB)
  65 ┤        ★ mxbai-embed-large ◄── BEST BANG FOR BUCK
     │        ★ gte-large-en-v1.5
     │        ★ bge-large-en-v1.5
  63 ┤          (~670 MB each)
     │
     │  ★ nomic-embed-text ◄── CURRENT (good for size, but outclassed)
  62 ┤    (274 MB)
     │
  60 ┤
     └────┬──────────┬──────────┬──────────┬──────► Model size
         137M      335M       7B         8B
        (tiny)   (small)   (medium)   (medium)
```

| Model | Size | MTEB | Context | In Ollama? | Best for |
|-------|------|------|---------|-----------|----------|
| **nomic-embed-text v1.5** | 274 MB | ~62.4 | 8K | Yes (official) | Minimal footprint, long docs |
| **mxbai-embed-large-v1** | 670 MB | ~64.7 | 512 | Yes (official) | Best quality in compact size |
| **snowflake-arctic-embed2** | 568 MB | ~55.6* | 8K | Yes (official) | Multilingual + long context |
| **bge-large-en-v1.5** | 670 MB | ~64.2 | 512 | Community only | Battle-tested workhorse |
| **gte-large-en-v1.5** | 670 MB | ~64.4 | 8K | Community only | Long context + high quality |
| **EmbeddingGemma** | ~200 MB | top <500M | 2K | Yes (official) | Smallest with modern quality |
| **nomic-embed-text-v2-moe** | ~300 MB | TBD | 8K | Yes (official) | Drop-in nomic upgrade |
| **Qwen3-Embedding-8B** | 4.7 GB | ~70.6 | 32K | Yes (official) | Maximum quality, no budget limit |

*\* snowflake score is retrieval-only, not full MTEB average*

### Recommendation

**The most practical upgrade: [mxbai-embed-large-v1](https://ollama.com/library/mxbai-embed-large)**

- +2.3 MTEB points over nomic (62.4 → 64.7) — that's a meaningful quality jump
- 1024 dimensions vs 768 — captures more stylistic nuance for voice comparison
- Only 670 MB — still tiny next to the 4.6 GB generation model
- Official Ollama support — just `ollama pull mxbai-embed-large`
- Its 512-token context limit is fine because our RAG chunks and eval comparisons are paragraph-level, not full documents

**If staying in the nomic ecosystem:** nomic-embed-text-v2-moe is a natural drop-in upgrade with the same long context but better quality.

**If quality is everything:** Qwen3-Embedding-8B (4.7 GB at Q4_K_M) is the current state-of-the-art open-source model, but running two ~5 GB models simultaneously needs careful memory management.

> **Important:** Switching embedding models means **re-embedding the entire ChromaDB corpus**. Vectors from different models live in incompatible vector spaces — you cannot mix them in the same collection.

---

## MTEB Benchmark

### What it is

**MTEB** (Massive Text Embedding Benchmark) is the standard leaderboard for comparing embedding models. Think of it as the "report card" for embedding models — it tests them across dozens of tasks and gives a single average score.

### Why it matters

When we compare nomic-embed-text (MTEB ~62.4) to mxbai-embed-large (MTEB ~64.7), that 2.3-point difference is measured on MTEB. Without a standard benchmark, we'd have no way to objectively compare embedding models.

### What it tests

```
MTEB tests embedding models on 8 task categories:

  ┌─────────────────────────────────────────────────┐
  │  1. Classification    - Sort text into categories│
  │  2. Clustering        - Group similar texts      │
  │  3. Pair Classification - Are two texts related? │
  │  4. Reranking         - Rank results by relevance│
  │  5. Retrieval         - Find relevant documents  │  ← Most relevant
  │  6. STS               - How similar are two texts│  ← for this project
  │  7. Summarization     - Identify good summaries  │
  │  8. BitextMining      - Match translations       │
  └─────────────────────────────────────────────────┘

  The MTEB "average" is the mean across all these tasks.
```

For this project, tasks 5 (Retrieval) and 6 (Semantic Textual Similarity) matter most — that's what we use embeddings for (RAG retrieval and style similarity measurement).

### How to read MTEB scores

- **55-60**: Decent, older or smaller models
- **60-63**: Good, competitive for size class (nomic-embed-text lives here)
- **63-66**: Strong, current best-in-class for compact models
- **66-71**: Excellent, requires 7B+ parameter models
- A **2-3 point** difference is meaningful and usually noticeable in practice

> **Further reading:** [MTEB Leaderboard on Hugging Face](https://huggingface.co/spaces/mteb/leaderboard) — the live benchmark leaderboard.

---

## LLM-as-Judge

### What it is

Using one LLM (like Gemini) to **evaluate** the output of another LLM (like Jacq's model). The judge reads the output and scores it.

### Why we replaced it

```
THE PROBLEM WITH LLM-AS-JUDGE (for this project)

Judge criteria: "Is it confident? Conversational? Engaging?"

Base Llama (unfine-tuned):              Jacq's fine-tuned model:
"Here's the thing about                "Look — I get it. You're
productivity — it's all                 reading another damn
about confidence!"                      productivity post and
                                        wondering why this one's
Score: 7.5/10                           gonna be different."
(Generically confident,
doesn't sound like Jacq)               Score: 6.8/10
                                        (Actually sounds like Jacq,
                                         but judge scored it lower!)
```

The judge scored against **generic style adjectives** ("confident", "conversational"), not Jacq-specific patterns. So the base model could win by being generically polished.

### What replaced it — three objective metrics

| Metric | What it measures | No subjectivity |
|--------|-----------------|-----------------|
| **Perplexity** | Does the model predict Jacq's words better? | Pure math |
| **Embedding similarity** | Does the output occupy the same style-space? | Vector comparison |
| **Failure mode detection** | Buzzword count, dash frequency, fragment % | Direct measurement |

### When LLM-as-Judge *does* work

LLM-as-Judge isn't inherently bad — it failed here because the judging criteria were too generic. It works well when:
- You have very specific, measurable rubric items (not "sounds confident")
- You're comparing outputs that are stylistically similar (not base vs. fine-tuned)
- You use it alongside objective metrics, not as the sole evaluator

---

# Part 5: Deployment — How Do We Ship and Serve It?

These concepts cover how we go from a trained model to one that runs efficiently and serves requests.

---

## Quantization and GGUF

### Quantization — making models fit in memory

Think of it like image compression. A raw photo might be 25 MB. A JPEG version is 2 MB. You lose a tiny bit of quality, but it's perfectly usable.

```
Precision levels:

fp32 (full precision)     ████████████████████████████████  32 bits per weight
                          Maximum quality. Maximum memory.

fp16 (half precision)     ████████████████                  16 bits per weight
                          Nearly identical quality. Half the memory.

Q4_K_M (4-bit)           ████                               4 bits per weight
                          Slight quality loss. 1/4 the memory of fp16.

     ┌──────────────────────────────────────────────┐
     │  Llama 3.1 8B at fp16:   ~16 GB              │
     │  Llama 3.1 8B at Q4_K_M: ~4.6 GB   ← We use │
     │  Quality difference: negligible for 8B        │
     └──────────────────────────────────────────────┘
```

The "K_M" in Q4_K_M means **mixed precision**: more important layers keep higher precision, less important layers get compressed more aggressively.

### GGUF — the file format

**GGUF** (GPT-Generated Unified Format) is the file format Ollama uses. Our pipeline:

```
Train LoRA     Fuse into      Convert to       Load in
adapters   →   base model  →  GGUF Q4_K_M  →   Ollama
(MLX)          (fp16)         (4.6 GB)         (serve)
```

> **Further reading:**
> - [Hugging Face: Introduction to Quantization](https://huggingface.co/blog/merve/quantization) — beginner-friendly blog post on quantization fundamentals.
> - [DeepLearning.AI: Quantization Fundamentals](https://www.deeplearning.ai/short-courses/quantization-fundamentals-with-hugging-face/) — free video short course.

---

## Safetensors

### What it is

A file format for storing model weights, created by Hugging Face. Used instead of PyTorch's `.pt` format because:
- **Faster to load** — uses memory mapping (loads only what's needed)
- **Safer** — `.pt` files can contain arbitrary executable code via Python's pickle format (security risk). Safetensors files contain only tensor data, no code.

### In this project

Adapter checkpoints are stored as `.safetensors` files: `adapters/jacq-v*/0000600_adapters.safetensors`.

---

## llama.cpp and Ollama

### llama.cpp

A C++ implementation of LLM inference that made it possible to run large language models on consumer hardware (laptops, phones) by implementing highly optimized inference code.

### Ollama

A user-friendly wrapper around llama.cpp. When you run `ollama run jacq:8b`, it's llama.cpp doing the actual text generation under the hood.

```
┌─────────────────────────────────────────────────┐
│  User / App                                     │
│       │                                         │
│       ▼                                         │
│  Ollama (friendly HTTP API, model management)   │
│       │                                         │
│       ▼                                         │
│  llama.cpp (optimized C++ inference engine)      │
│       │                                         │
│       ▼                                         │
│  GGUF file (jacq-v6-8b-q4km.gguf, 4.6 GB)      │
└─────────────────────────────────────────────────┘
```

GGUF is llama.cpp's native file format — that's why we convert our trained model to GGUF.

In this project, Ollama runs **on-demand** via `OllamaManager` — it starts when the app needs generation and stops when done, so it doesn't consume memory when idle.

---

# Part 6: Advanced Patterns

---

## RAG (Retrieval-Augmented Generation)

### What it is

A technique that **retrieves relevant documents** from a knowledge base and includes them in the model's prompt. Think of it like giving a student an open-book exam — they can look things up.

### How it works

```
Step 1: User asks         Step 2: Search             Step 3: Generate
┌─────────────────┐      ┌──────────────────┐       ┌──────────────────┐
│ "What did Jacq  │      │  ChromaDB finds  │       │  Model reads the │
│  write about    │─────►│  the 3 most      │──────►│  retrieved docs  │
│  Sedona?"       │      │  similar blog    │       │  + the question  │
│                 │      │  posts           │       │  and generates   │
└─────────────────┘      └──────────────────┘       │  an answer       │
                                                    └──────────────────┘
    Query → Embedding → Vector search → Top matches → Augmented prompt → Response
```

### Vector databases — where RAG stores its knowledge

A **vector database** (ChromaDB in our case) is a specialized database that stores text as embedding vectors and lets you search by *similarity* instead of exact keyword matching.

```
Traditional database:                Vector database:
┌────────────────────────┐          ┌────────────────────────┐
│  SELECT * FROM posts   │          │  "Find posts similar   │
│  WHERE title LIKE      │          │   to: 'morning routine │
│  '%morning%'           │          │   struggles'"          │
│                        │          │                        │
│  Only finds exact      │          │  Finds posts about     │
│  keyword matches       │          │  waking up, habits,    │
│                        │          │  productivity — even   │
│                        │          │  if they never say     │
│                        │          │  "morning"             │
└────────────────────────┘          └────────────────────────┘
```

### Components in this project

| Component | Role |
|-----------|------|
| **ChromaDB** | Vector database storing Jacq's writing as embeddings |
| **nomic-embed-text** | Converts text to vectors for search |
| **Retriever class** | Handles the query → retrieve → format pipeline |

### The critical lesson: RAG hurts voice generation

This is counterintuitive — more data should help, right? Not for style:

```
WITHOUT RAG (model relies on fine-tuning)    WITH RAG (model gets raw corpus chunks)
┌───────────────────────────────────┐       ┌───────────────────────────────────┐
│  Buzzwords:  4.8  ✓ Natural      │       │  Buzzwords:  11.1  ✗ Doubled!    │
│  Embed sim:  0.75 ✓ Sounds like  │       │  Embed sim:  0.67  ✗ LESS like   │
│                     Jacq         │       │                      Jacq        │
│  Specificity: 5.2 ✓ Fresh ideas │       │  Specificity: 3.9  ✗ Parroting  │
│  Dashes:     12.9 ✓ In range    │       │  Dashes:     17.4  ✗ Overshot   │
└───────────────────────────────────┘       └───────────────────────────────────┘
```

**Why:** Retrieved chunks carry all the "journey/authentic/intentional" language from the raw corpus. The model stitches them in as Frankenstein text instead of generating naturally from its fine-tuned voice.

**Rule of thumb:**
- RAG for **facts** (names, dates, events): YES
- RAG for **voice/style** generation: NO

> **Further reading:** [AWS: What is RAG?](https://aws.amazon.com/what-is/retrieval-augmented-generation/) — clean conceptual overview with diagrams.

---

# Appendix

## Further Reading

### Video courses (start here if you're visual)
- [3Blue1Brown: Neural Networks](https://www.3blue1brown.com/topics/neural-networks) — the best visual introduction to how neural networks learn
- [DeepLearning.AI: Quantization Fundamentals](https://www.deeplearning.ai/short-courses/quantization-fundamentals-with-hugging-face/) — free short course on quantization

### Illustrated guides
- [Jay Alammar: Visualizing Machine Learning One Concept at a Time](https://jalammar.github.io/) — the "Illustrated Transformer", "Illustrated Word2vec", and more
- [Jay Alammar: The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) — how attention and transformers work, with diagrams

### Interactive courses
- [Google ML Crash Course](https://developers.google.com/machine-learning/crash-course/overfitting) — interactive lessons with visualizations
- [Hugging Face LLM Course](https://huggingface.co/learn/llm-course/en/chapter2/4) — hands-on course covering tokenization, fine-tuning, and more

### Benchmarks
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) — live embedding model benchmark rankings

### Reference
- [Prompt Engineering Guide: LLM Settings](https://www.promptingguide.ai/introduction/settings) — temperature, top-p, and other generation parameters
- [Hugging Face: Perplexity](https://huggingface.co/docs/transformers/en/perplexity) — technical reference for the perplexity metric
- [Sebastian Raschka: LoRA and DoRA from Scratch](https://magazine.sebastianraschka.com/p/lora-and-dora-from-scratch) — build LoRA from scratch in code
