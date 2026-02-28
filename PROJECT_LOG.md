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
