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

---

## Training Version History

### v1 — Initial Baseline (2026-02-28)

**Config:**
- Model: Llama 3.1 8B Instruct 4-bit
- LoRA: rank=8, alpha=16, layers=16
- Learning rate: 1e-5, batch_size=1, max_seq_length=1024
- Iterations: 600 (~0.87 epochs over 691 examples)
- grad_checkpoint: true

**Results:**
- Final train loss: 2.029
- Val loss: 2.086
- Peak memory: 6.4 GB
- Speed: ~549 tokens/sec

**Evaluation (Gemini 2.5 Flash judge):**
- Overall: 6.7/10 (vs baseline 5.3/10)
- Vocabulary overlap: 0.23 (vs baseline 0.18)
- ROUGE-1: 0.43 (vs baseline 0.37)
- Avg sentence length: 20.3 words (reference: 16.5)

**Findings:**
- Undertrained — only saw ~87% of training data once
- Voice was present but inconsistent
- Model still overshooting sentence length (20.3 vs Jacq's 16.5)

**Checkpoint used:** Final (iter 600)

---

### v2 — 3-Epoch Experiment (2026-02-28)

**Config:**
- Same as v1 except: 3 epochs
- LoRA: rank=8, alpha=16

**Results:**
- Val loss: 1.520
- Lower loss than v1 but voice quality degraded

**Evaluation:**
- Overall: 6.7/10 (no improvement over v1)
- Voice over-smoothed — lost Jacq's edge, directness, and stylistic quirks
- Model averaged out distinctive features into blander prose

**Key Lesson:** 3 epochs is too many for an 8B model on this dataset. The model memorizes surface patterns and smooths out the voice. 2 epochs became the standard.

---

### v3 — Qwen 14B Experiment (2026-02-28)

**Config:**
- Model: Qwen 2.5 14B (switch from Llama)
- 3 epochs
- Same LoRA config

**Results:**
- Val loss: 1.533
- Overall: 2.5/10

**Evaluation:**
- Catastrophic failure
- Qwen's safety training fought the LoRA adaptation
- Model broke character constantly, reverted to assistant-speak
- Output read like a corporate FAQ, not Jacq's voice

**Key Lesson:** Qwen 2.5 14B is a bad base for voice cloning. Its aggressive safety training overrides LoRA's influence. Llama 3.1 is naturally conversational and easy to steer. Abandoned Qwen entirely.

---

### v4 — Production Baseline (2026-02-28)

**Config:**
- Model: Llama 3.1 8B Instruct 4-bit
- LoRA: rank=16, alpha=32, layers=16 (doubled from v1-v3)
- Learning rate: 1e-5, batch_size=1, max_seq_length=2048 (doubled from v1)
- 2 epochs (1382 iterations)
- Checkpoint frequency: every 100 steps

**Results:**
- Train loss: 1.460
- Val loss: 1.507
- Train-val gap: 0.047 (best generalization of any version)
- Peak memory: 7.8 GB

**Evaluation (Gemini judge):**
- Overall: 7.0/10 (best at the time, beat v1's 6.9)
- Better sentence rhythm, vocabulary, and structure

**Key Changes from v1:**
- Doubled LoRA rank (8→16) and alpha (16→32) — more adapter capacity
- Doubled max_seq_length (1024→2048) — model sees full blog posts
- 2 epochs instead of <1 — proper training duration

**Key Lesson:** Doubling LoRA capacity and sequence length was the right move. 2 epochs gave excellent generalization (gap of only 0.047).

---

### v5 — Data Cleanup & Prompt Rewrite

**Config:**
- Model: Llama 3.1 8B Instruct 4-bit
- LoRA: rank=16, alpha=32, layers=16
- Learning rate: 1e-5, batch_size=1, max_seq_length=2048
- 2 epochs (934 iterations on ~467 train examples)
- Checkpoint frequency: every 100 steps

**Changes from v4:**
1. **Removed podcast transcripts** — 142 examples dropped. Podcast transcripts had near-zero dashes (0.3/1k words) and no sentence fragments, actively diluting the written voice. This was the single biggest data quality fix.
2. **Rewrote system prompt** — Updated with accurate style statistics measured from her actual writing:
   - Dashes: 7-14 per 1,000 words
   - Sentence fragments: ~15%
   - Profanity: ~40% of posts contain mild profanity
   - Conjunction starters: And, But, So, Or
   - Previous prompt had wrong claims that created contradictory training signals
3. **Added style exemplars** — Top 20 blog posts ranked by "Jacq-ness" score + 15 hand-crafted style anchors (`data/training/exemplars.jsonl`, built by `scripts/build_exemplars.py`)

**Results:**
- Val loss: ~1.15
- Training examples: ~467 (down from 691 after podcast removal)

**Evaluation (new objective metrics — replaced Gemini judge):**
- Buzzwords: 5.1 (measured count per piece)
- Embedding similarity: 0.70
- Specificity: 5.2
- Dashes: 12.89/1k words
- Fragments: ~8%

**RAG experiment (v5):**
- RAG ON: buzzwords 11.1, embed sim 0.67, specificity 3.9, dashes 17.36
- RAG OFF: buzzwords 5.1, embed sim 0.70, specificity 5.2, dashes 12.89
- Conclusion: RAG poisons voice generation. Turned OFF by default for all generation tasks.

**Evaluation system overhaul:**
- Replaced LLM-as-judge (Gemini) with 3 objective metrics:
  1. Perplexity (MLX) — does the model predict Jacq's words better?
  2. Embedding similarity (nomic-embed-text) — does output occupy the same style-space?
  3. Failure mode detection — targeted counts of buzzwords, dashes, fragments
- Reason: Gemini judge scored against generic style adjectives, so the base model could score higher by being generically "confident" even though it sounded nothing like Jacq

---

### v6 — Buzzword Filtering (Current Production)

**Config:**
- Model: Llama 3.1 8B Instruct 4-bit
- LoRA: rank=16, alpha=32, layers=16, dropout=0.05
- Learning rate: 1e-5, batch_size=1, max_seq_length=2048
- 2 epochs (916 iterations on 458 train examples)
- Checkpoint frequency: every 100 steps
- Validation: every 50 steps, 25 batches

**Changes from v5:**
1. **Training data buzzword filter** — Added to `build_training_data.py`: drops examples with primary buzzword count >= 6 or total >= 10. Dropped 11 of 584 examples, 573 surviving, 458 train / 57 valid / 58 test split.
2. **System prompt cleanup** — Replaced buzzy theme/value labels:
   - "intentional living" → "doing things on purpose"
   - "authenticity" → "writing that sounds like a real person"
   - Added crutch word rule: journey/intentional/authentic once per piece max
   - Expanded banned jargon list to 13 terms

**Results:**
- Best val loss: 1.138 at iteration 600
- Train-val gap: 0.083 at best checkpoint
- Overfitting onset after iteration 700+
- Peak memory: 7.8 GB
- Speed: ~534 tokens/sec

**Evaluation (v6 vs v5):**

| Metric | v5 | v6 | Target | Status |
|--------|-----|-----|--------|--------|
| Buzzwords | 5.1 | 4.8 | <5 | Met |
| Embedding similarity | 0.70 | 0.75 | >0.70 | Met |
| Specificity | 5.2 | 5.1 | >5 | Met |
| Dashes | 12.89 | 16.14/1k | 7-14 | Over target |
| Fragments | ~8% | 8.72% | ~15% | Under target |
| Directness | — | 4.1/5 | >4.3 | Under target |

**Best checkpoint:** Iteration 600 (NOT the final iteration 916)
- Copied: `cp adapters/jacq-v6/0000600_adapters.safetensors adapters/jacq-v6/adapters.safetensors`

**GGUF export:**
- Fuse: `mlx_lm fuse` → `models/fused/jacq-v6-8b-fused/`
- Dequant: `mlx_lm convert --dtype float16` → `models/fused/jacq-v6-8b-fp16/`
- GGUF: `mlx_lm gguf --q-type Q4_K_M` → `models/fused/jacq-v6-8b-q4km.gguf` (4.6 GB)
- Import: `ollama create jacq-v6:8b -f Modelfile`

**Remaining issues for v7:**
- Dashes 16.14/1k (target 7-14) — overshooting
- Fragments 8.72% (target ~15%) — undershooting
- Directness 4.1/5 (baseline 4.3) — slightly below baseline

---

### Training Version Summary

| Version | Model | Epochs | Iters | Val Loss | Gap | Score | Notes |
|---------|-------|--------|-------|----------|-----|-------|-------|
| v1 | Llama 8B | ~0.87 | 600 | 2.086 | — | 6.9 | Undertrained baseline |
| v2 | Llama 8B | 3 | — | 1.520 | — | 6.7 | Over-smoothed voice |
| v3 | Qwen 14B | 3 | — | 1.533 | — | 2.5 | Qwen fought fine-tuning |
| v4 | Llama 8B | 2 | 1382 | 1.507 | 0.047 | 7.0 | Best generalization |
| v5 | Llama 8B | 2 | 934 | ~1.15 | — | — | Podcasts removed, prompt rewrite |
| v6 | Llama 8B | 2 | 916 | 1.138 | 0.083 | — | **Current production** |

### Cumulative Lessons Learned

1. **2 epochs is the sweet spot** for Llama 8B on ~460 examples — 3 epochs over-smooths
2. **Qwen is a bad base for voice cloning** — safety training overrides LoRA
3. **Llama 3.1 8B is naturally conversational** and easy to steer with LoRA
4. **System prompt accuracy matters enormously** — wrong claims create contradictory training signals
5. **Train = serve alignment is critical** — system prompt must match between training and inference
6. **Podcast transcripts actively dilute written voice** — near-zero dashes, no fragments
7. **RAG poisons voice generation** — use only for factual retrieval, never for style
8. **Best checkpoint is often NOT the final one** — always check val loss curve
9. **Training data quality > quantity** — removing 11 bad examples improved output more than adding 100 average ones
10. **LLM-as-judge is unreliable for voice evaluation** — objective metrics (perplexity, embedding similarity) are more trustworthy
11. **LoRA rank 16 > rank 8** for voice cloning — more adapter capacity needed to capture stylistic nuance
12. **Buzzword contamination propagates** — if 65% of training data has buzzwords, the model will generate them regardless of prompt instructions

---

## 2026-03-01 — LinkedIn Content Repurposing (Feature Implementation)

### What was built
LinkedIn post generator — takes a blog post URL, fetches the content, and generates a standalone LinkedIn post (150-300 words) in Jacq's voice using the fine-tuned model.

### Files created/modified
- `prompts/linkedin.txt` — LinkedIn-specific prompt template (algorithm rules, content rules, voice rules)
- `app/assistant.py` — Added `"linkedin"` task type, URL fetching via Squarespace JSON API + HTML fallback, LinkedIn-specific system prompt override, max_tokens cap (512), post-processing cleanup
- `app/web.py` — Added LinkedIn task type to UI, URL input field, Post to LinkedIn button, word/character counter, temperature default (0.6 for LinkedIn)
- `app/linkedin_client.py` — LinkedIn API client (OAuth2, post creation via `/rest/posts`)
- `scripts/linkedin_auth.py` — One-time OAuth2 flow script

### LinkedIn API Details
- API version: `202507`
- Endpoint: `POST https://api.linkedin.com/rest/posts`
- Author format: `urn:li:person:{sub}` where `sub` comes from `/v2/userinfo` OpenID endpoint
- Required scopes: `openid`, `w_member_social`
- Credentials: `credentials/linkedin_credentials.json`, `credentials/linkedin_token.json`

### Voice Quality Findings
- Temperature 0.3: Too harsh — lost Jacq's warmth and personality
- Temperature 0.5: Decent but flat
- **Temperature 0.6: Sweet spot** — warm enough for voice, controlled enough for constraints
- Temperature 0.7: Hallucinated details
- max_tokens capped at 512 for LinkedIn (enforces 150-300 word range)
- Model struggles with distillation — tends to write full blog posts instead of condensing

### LinkedIn Algorithm Strategy
- Native-first: standalone posts deliver full value without linking out
- LinkedIn penalizes external links by ~60% reach
- Posts end with engagement question + 3-5 hashtags
- Profile bio/featured section drives click-through (appears as "direct" in GA4)

### Status
- LinkedIn posting: working (first post published successfully)
- OAuth: token expires ~2 months, re-auth via `scripts/linkedin_auth.py`

---

## Phase Status
- [x] Phase 1: Environment Setup
- [x] Phase 2: Data Pipeline
- [x] Phase 3: Prompt Engineering Baseline
- [x] Phase 4: Fine-Tuning (v6 — current production)
- [x] Phase 5: Writing Assistant App (Gradio web UI + CLI)
- [x] Phase 6: Evaluation (objective metrics: perplexity, embedding similarity, failure modes)
- [x] LinkedIn Content Repurposing (P0 feature — blog URL → LinkedIn post → API posting)
