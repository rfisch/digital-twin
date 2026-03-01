# Project Log — Digital Twin Writing Assistant

Research journal, decisions, and progress tracking.

---

## 2026-02-27 — Project Kickoff

### Decisions Made
- **Base model**: Llama 3.1 8B Instruct (4-bit quantized via MLX) for fast iteration
- **Fine-tuning**: MLX (mlx-lm) — native Apple Silicon, uses unified memory
- **Inference**: Ollama — easy API, model management
- **RAG**: ChromaDB + Ollama nomic-embed-text — local embeddings + vector search
- **Hardware**: Mac Studio M3 Ultra, 96GB unified memory

### Why This Stack
- MLX is the fastest option for training on Apple Silicon (no CPU↔GPU copies)
- Ollama handles model serving cleanly, separate from training
- Fine-tuning captures voice/style, RAG provides content/facts
- Start with 8B for fast iteration, scale to 70B once pipeline is validated

### Phase 1 Complete
- [x] Python 3.12.8 via pyenv
- [x] Ollama installed and running
- [x] MLX and dependencies installed
- [x] Base models pulled (llama3.1:8b, nomic-embed-text)
- [x] Project structure created

---

## Training Data Strategy

### Format
Chat JSONL with system/user/assistant messages. System prompt encodes Jacq's style.

### Sources
- Blog posts: use real title as prompt, real post as response
- Book excerpts: use 8B model to generate plausible prompts for each passage

### Target
500–2000 high-quality training examples

---

## Hyperparameter Notes

Starting configuration (to be tuned):
- LoRA rank: 8, alpha: 16
- Learning rate: 1e-5
- Batch size: 4
- Iterations: 600
- Max sequence length: 2048

Rationale: Conservative starting point. Rank 8 is enough for style transfer. Low LR to avoid catastrophic forgetting.

---

## 2026-02-28 — Data Pipeline & Training Complete

### Data Pipeline Results
- **Raw content**: 5 books, 304 blog posts (DOCX), 22 podcast transcripts (DOCX)
- **Cleaning**: 331 files cleaned, ~3.96M characters
- **Style analysis**: 710K words, 53K sentences, 15.5K unique words
- **Training examples**: 864 total (304 blog, 245 book, 315 podcast)
- **Split**: 691 train / 86 valid / 87 test

### Training Attempts

**Attempt 1** — batch_size=4, seq_len=2048, no grad_checkpoint
- Crashed at iter 20 with Metal GPU error, peak mem 62.4 GB
- Error: `kIOGPUCommandBufferCallbackErrorInnocentVictim`

**Attempt 2** — batch_size=2, seq_len=2048, grad_checkpoint=true
- Crashed at iter 70, peak mem 10.6 GB
- Same Metal command buffer timeout (not a memory issue — GPU timeout)

**Attempt 3 (SUCCESS)** — batch_size=1, seq_len=1024, grad_checkpoint=true
- All 600 iterations completed
- Peak memory: 6.4 GB
- Speed: ~549 tokens/sec, ~0.55 it/sec
- Final train loss: 2.029, val loss: 2.086
- Best val loss: ~2.045 around iter 450-550
- 12 checkpoints saved (every 50 iterations)

### Key Lesson
Metal GPU crashes are command buffer timeouts, not strictly memory issues. Reducing both batch_size AND max_seq_length eliminated the problem.

### Final Config (configs/lora_config.yaml)
- batch_size: 1
- max_seq_length: 1024
- grad_checkpoint: true
- Everything else as originally planned

---

## 2026-02-28 — Model Export & Ollama Import

### GGUF Export Challenge
MLX 4-bit quantized models cannot be directly exported to GGUF:
- `mlx_lm.fuse --export-gguf` → "Conversion of quantized models is not yet supported"
- llama.cpp `convert_hf_to_gguf.py` → "Quant method is not yet supported: None"

### Solution: Dequantize → GGUF
1. Fused adapter into base model: `mlx_lm fuse --dequantize` → fp16 safetensors (16 GB)
2. Converted fp16 to GGUF via llama.cpp: `convert_hf_to_gguf.py` → 16 GB GGUF
3. Imported into Ollama: `ollama create jacq:8b -f Modelfile` → Success

### Model Files
- `adapters/jacq-v1/` — LoRA adapter checkpoints (12 snapshots)
- `models/fused/jacq-8b-mlx/` — 4-bit fused MLX model (4.2 GB)
- `models/fused/jacq-8b-fp16/` — Dequantized fp16 safetensors (16 GB, intermediate)
- `models/fused/jacq-8b-f16.gguf` — GGUF for Ollama (16 GB, fp16)
- Ollama model: `jacq:8b` (16 GB)

### First Test
Prompt: "Write a short blog post about why morning routines matter for creative women."
Result: Conversational, personal, first-person blog post with specific anecdotes. Uses phrases like "sacred practice", "nourishing my body and brain", "create with intention" — feels authentic to Jacq's voice.

### Quantization
Installed cmake 4.2.3, built llama.cpp quantize tool, compressed fp16 GGUF (16 GB) to Q4_K_M (4.6 GB).
Automated export pipeline: `scripts/export_model.py`

---

## 2026-02-28 — Phase 3: Baseline Comparison

### System Prompt
Updated `prompts/system_prompt.txt` with real style data from analyze_style.py:
- Sentence patterns, punctuation stats, vocabulary preferences
- Added "About Jacq" section with real personal details (podcast name, family, habits, values)
- This fixed hallucination issues (model now correctly uses "How Women Write" instead of inventing names)

### Comparison
Ran 12 prompts across blog, email, copywriting, personal, and advice categories.
- Base model (llama3.1:8b + system prompt) vs fine-tuned (jacq:8b)
- Fine-tuned model writes ~30% longer, uses more sentence fragments and personal anecdotes
- Base model tends toward generic "blogger voice"
- Fine-tuned model occasionally hallucinates details (mitigated by RAG + personal bio)
- Results: `evaluation/baseline/comparison_report.md`

---

## 2026-02-28 — Phase 5: Writing Assistant App

### RAG Pipeline
- Ingested 331 files → 2,009 chunks into ChromaDB via nomic-embed-text
- Retriever returns highly relevant excerpts grounded in Jacq's actual writing
- Fixed ChromaDB v1.5 API changes, fixed relative path issues

### Integration Testing
- CLI (`python app/cli.py blog "topic"`) — working end-to-end with RAG
- Web UI (`python app/web.py`) — Gradio 6 API fixes applied, builds cleanly
- Fixed model override bug in web.py (was applied after generation instead of before)
- All components use on-demand Ollama via OllamaManager

### Personal Bio in System Prompt
Added extensive "About Jacq" section to both `prompts/system_prompt.txt` and `Modelfile`.
Baked into Ollama model via `ollama create jacq:8b -f Modelfile`.

---

## 2026-02-28 — Phase 6: Evaluation

### Automated Evaluation (10 test examples)
Using held-out test set examples (Jacq's real writing as reference).

**LLM-as-Judge scores (llama3.1:8b judging):**

| Criterion | Fine-tuned | Baseline | Delta |
|-----------|-----------|----------|-------|
| Tone | 6.5 | 6.8 | -0.3 |
| Structure | 5.2 | 5.2 | 0.0 |
| Vocabulary | 8.3 | 8.0 | +0.3 |
| Authenticity | 4.9 | 4.9 | 0.0 |
| **Overall** | **6.55** | **6.47** | **+0.1** |

**Style metrics (fine-tuned wins clearly):**

| Metric | Reference | Fine-tuned | Baseline |
|--------|-----------|-----------|----------|
| Avg sentence length | 16.5 words | 22.3 words | 21.3 words |
| Vocabulary overlap | — | 0.25 | 0.17 |
| ROUGE-1 F1 | — | 0.48 | 0.36 |

### Key Findings
1. **Vocabulary overlap** is 47% higher for the fine-tuned model (0.25 vs 0.17) — it uses more of Jacq's actual words
2. **ROUGE-1** is 33% higher (0.48 vs 0.36) — more textual similarity to Jacq's real writing
3. **LLM judge scores are close** (6.55 vs 6.47) — but the judge is the same base model, which may not reliably detect style nuance
4. Both models write longer sentences than Jacq (22 vs 16.5 words) — the fine-tuned model hasn't fully learned her punchy short-sentence style
5. The fine-tuned model's biggest standout: Example 9 ("Finding your way") scored 7/10 vs 4/10 baseline

### Improvement Opportunities
- Train for more iterations (2-3 epochs) to better capture sentence length patterns
- Add more short-sentence examples to training data
- Use a larger/different model as judge (llama3.1:8b judging itself has bias)
- More training data focused on blog posts specifically (highest-value output type)

---

## 2026-02-28 — Gemini External Judge (Re-evaluation)

Replaced self-judging llama3.1:8b with Gemini 2.5 Flash as external judge. This eliminates the bias of a model grading its own output.

**LLM-as-Judge scores (Gemini 2.5 Flash judging):**

| Criterion | Fine-tuned | Baseline | Delta |
|-----------|-----------|----------|-------|
| Tone | 6.8 | 5.7 | +1.1 |
| Structure | 6.0 | 5.3 | +0.7 |
| Vocabulary | 7.3 | 5.1 | +2.2 |
| Authenticity | 6.5 | 4.9 | +1.6 |
| **Overall** | **6.7** | **5.3** | **+1.4** |

**Style metrics:**

| Metric | Reference | Fine-tuned | Baseline |
|--------|-----------|-----------|----------|
| Avg sentence length | 16.5 words | 20.3 words | 24.0 words |
| Vocabulary overlap | — | 0.23 | 0.18 |
| ROUGE-1 F1 | — | 0.43 | 0.37 |

### Key Findings (Gemini Judge)
1. **Fine-tuned model clearly wins** — 6.7 vs 5.3 overall (+1.4 points), compared to the negligible +0.1 with self-judging
2. **Vocabulary is the biggest win** — +2.2 point delta. The fine-tuned model uses Jacq's actual words and phrases
3. **Authenticity gap** — +1.6 points. Gemini rates the fine-tuned output as significantly more believable as Jacq's writing
4. **Example 3 (Wishbeads guest post)** — largest gap: 7/10 vs 2/10. The baseline wrote a generic third-person piece while the fine-tuned model wrote in Jacq's first-person style
5. **Sentence length** — Fine-tuned (20.3) is closer to Jacq's reference (16.5) than baseline (24.0), but still overshoots
6. **Common critique from Gemini** — both models underuse rhetorical questions, paragraph starters ("And", "But", "So"), and occasional profanity

### Self-Judge vs External Judge Comparison
- llama3.1:8b judging: +0.1 delta (6.55 vs 6.47) — nearly indistinguishable
- Gemini 2.5 Flash judging: +1.4 delta (6.7 vs 5.3) — clear differentiation

This confirms the self-judging bias hypothesis. The base model rated its own output nearly as high as the fine-tuned output. An external judge sees the difference clearly.

---

## Phase Status
- [x] Phase 1: Environment Setup
- [x] Phase 2: Data Pipeline
- [x] Phase 3: Prompt Engineering Baseline
- [x] Phase 4: Fine-Tuning
- [x] Phase 5: Writing Assistant App
- [x] Phase 6: Evaluation (initial run complete, iteration ongoing)
