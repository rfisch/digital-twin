# Fine-Tuning Guide — Understanding the Training Process

## What's Happening During Training

We're using **QLoRA** (Quantized Low-Rank Adaptation) to teach a pre-trained language model (Llama 3.1 8B) to write in Jacq's voice. Rather than retraining the entire 8 billion parameter model — which would require hundreds of gigabytes and days of compute — we're training a small set of adapter weights (~10.5 million parameters, 0.13% of the model) that steer the model's outputs toward Jacq's style.

Think of it like this: the base model already knows English, grammar, how to write blog posts, etc. The LoRA adapter is a "voice filter" layered on top that shifts the model's word choices, sentence patterns, and tone to match Jacq's.

### The Training Loop

Each iteration of training follows this cycle:

1. **Sample a training example** — Pick a prompt/response pair from the training data (e.g., "Write a blog post about morning routines" → Jacq's actual blog post)
2. **Forward pass** — Feed the prompt through the model and generate a prediction for what the next token should be at every position
3. **Compute loss** — Compare the model's predictions against Jacq's actual words. The "loss" is a number measuring how wrong the model's predictions were
4. **Backward pass** — Calculate how to adjust the adapter weights to reduce the loss
5. **Update weights** — Apply those adjustments (scaled by the learning rate)
6. **Repeat** — Do this 600 times across different training examples

---

## Understanding the Training Output

### Loss Values

```
Iter 10:  Train loss 2.512
Iter 20:  Train loss 2.191
Iter 30:  Train loss 2.035
Iter 50:  Train loss 2.133  |  Val loss 2.140
Iter 70:  Train loss 1.979
Iter 100: Train loss 2.125  |  Val loss 2.182
```

**What is loss?** Loss measures how surprised the model is by Jacq's actual word choices. Technically it's the cross-entropy between the model's predicted probability distribution and the actual next token. In practical terms:

- **Higher loss (3.0+)** — The model's predictions are far from Jacq's actual writing. It doesn't "get" her voice yet.
- **Lower loss (1.5-2.0)** — The model is making predictions that closely match Jacq's actual word choices. It's learning her patterns.
- **Very low loss (<1.0)** — Potentially memorizing the training data rather than learning general patterns (overfitting — see below).

**Why is it dropping?** Each iteration adjusts the adapter weights to make the model slightly better at predicting Jacq's next word. Over hundreds of iterations, these small improvements compound. The model progressively learns her vocabulary preferences, sentence structure, transitions, tone, and thematic patterns.

### Train Loss vs. Validation Loss

These are the two most important numbers to watch:

- **Train loss** — How well the model predicts the data it's actively training on. This should consistently decrease.
- **Val loss** — How well the model predicts data it has *never seen* during training (the validation set). This is the true measure of whether the model is learning generalizable patterns.

**What to look for:**

| Pattern | What It Means | Action |
|---------|--------------|--------|
| Both dropping | Model is learning well | Keep training |
| Train drops, Val flat | Starting to memorize (mild overfitting) | Consider stopping soon |
| Train drops, Val rises | Overfitting — memorizing, not generalizing | Stop training, use earlier checkpoint |
| Both flat | Model has plateaued | Try higher learning rate or more data |
| Both erratic | Learning rate too high | Reduce learning rate |

In our run, both train and val loss dropped from ~2.9 to ~2.1 through the first 100 iterations, which is healthy convergence.

### Memory Usage

```
Peak mem 6.376 GB
```

This is GPU memory (unified memory on Apple Silicon). Our setup:

- **Base model** — Llama 3.1 8B at 4-bit quantization uses ~4.5 GB
- **LoRA adapters** — The trainable parameters add ~0.1 GB
- **Activations & gradients** — The intermediate values during training use ~1.5 GB
- **Total** — ~6.4 GB of our 96 GB available

The `grad_checkpoint: true` setting trades compute time for memory savings — instead of storing all intermediate values in memory, it recomputes them during the backward pass. This is why memory dropped from 62 GB (first attempt) to 6.4 GB.

### Tokens Per Second

```
Tokens/sec 548.127
```

This is the speed of training — how many text tokens the model processes per second. Higher is better. On the M3 Ultra this translates to roughly 0.55 iterations per second, meaning:

- 600 iterations ÷ 0.55 it/sec ≈ **~18 minutes of training time** (plus validation pauses)
- Total wall time including validation: **~25-30 minutes**

### Checkpoints

```
Iter 50: Saved adapter weights to adapters/jacq-v1/adapters.safetensors
Iter 100: Saved adapter weights to adapters/jacq-v1/0000100_adapters.safetensors
```

The training saves adapter weights every 50 iterations. This means:
- If training crashes, we can resume from the last checkpoint
- If later iterations overfit, we can go back to an earlier checkpoint that generalized better
- `adapters.safetensors` is always the latest checkpoint
- `0000050_adapters.safetensors`, `0000100_adapters.safetensors`, etc. are numbered snapshots

---

## Hyperparameter Choices Explained

### configs/lora_config.yaml

```yaml
model: "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
```
The base model. 4-bit quantization compresses the model from 16 GB to ~5 GB with minimal quality loss.

```yaml
lora_layers: 16
lora_rank: 8
lora_alpha: 16
```
- **lora_layers: 16** — How many of the model's 32 transformer layers get LoRA adapters. 16 is the top half, which controls higher-level style and content decisions.
- **lora_rank: 8** — The "capacity" of each adapter. Rank 8 is small but sufficient for style transfer. Higher rank = more expressive but more prone to overfitting.
- **lora_alpha: 16** — Scaling factor. Alpha/rank = 2.0 is a standard ratio that balances adapter influence with the base model's knowledge.

```yaml
learning_rate: 1.0e-5
```
How much to adjust weights per iteration. 1e-5 is conservative — it learns slowly but avoids "catastrophic forgetting" (destroying the base model's general knowledge). If loss plateaus, we could try 2e-5 or 5e-5.

```yaml
batch_size: 1
```
Process one training example per iteration. Larger batches average gradients across multiple examples (smoother learning) but use more memory. We're using 1 for GPU stability.

```yaml
max_seq_length: 1024
```
Maximum token length per training example. Longer sequences use more memory. Our first runs at 2048 crashed the GPU; 1024 tokens ≈ 750 words, which captures the structure of most blog posts and book passages.

```yaml
iters: 600
```
Total training iterations. With 691 training examples and batch_size 1, 600 iterations means the model sees most of the training data once. For style transfer, 1-3 epochs (passes through the data) is usually the sweet spot.

---

## How We Ensure Quality

### 1. Training Data Quality (Garbage In, Garbage Out)
The most important factor. Our training data is:
- 304 real blog posts with natural prompt/response structure
- 245 book passages with LLM-generated prompts
- 315 podcast transcript chunks
- All validated: minimum 50 words, proper message format

### 2. Validation Monitoring
Every 50 iterations, we measure loss on held-out data the model hasn't seen. If val loss starts rising while train loss drops, we're overfitting and should stop.

### 3. Checkpointed Rollback
We save adapter weights every 50 iterations. After training completes, we can test different checkpoints and pick the one that produces the best output — not necessarily the last one.

### 4. Evaluation Pipeline (Post-Training)
`scripts/evaluate.py` runs automated evaluation:
- **Style metrics** — Does the output match Jacq's sentence length distribution, vocabulary overlap, punctuation patterns?
- **ROUGE scores** — How much textual overlap exists between generated and real writing?
- **LLM-as-judge** — A separate model rates the output 1-10 on tone, structure, vocabulary, and authenticity
- **A/B comparison** — Fine-tuned model vs. base model on the same prompts

### 5. Human Review
The ultimate test — can Jacq (or people who know her writing) tell the difference between AI-generated and real? The test set (87 held-out examples) provides reference material for blind comparison.

---

## What "Good" Looks Like

After training, a successful fine-tune will show:
- Train loss settled between **1.5-2.2** (learned patterns without memorizing)
- Val loss within **0.1-0.3** of train loss (generalizing well)
- Generated text that uses Jacq's characteristic phrases, sentence rhythm, and tone
- Content that feels authentic to people familiar with her writing
- The model stays coherent and on-topic (base model capabilities preserved)

A fine-tune that needs more work will show:
- Generated text that is grammatically correct but sounds generic
- Over-repetition of certain phrases (overfitting to common training patterns)
- Val loss significantly higher than train loss (poor generalization)
- Loss of coherence or factual grounding (catastrophic forgetting)

---

## After Training: Getting the Model Into Ollama

Training produces LoRA adapter weights — a small file (~40 MB) that modifies the base model's behavior. But Ollama can't use adapter files directly. It needs a single, self-contained model file in GGUF format. Getting from adapter weights to a working Ollama model requires three conversion steps, each with a specific reason.

### The Pipeline at a Glance

```
LoRA adapter (.safetensors, ~40 MB)
    ↓  Step 1: Fuse — bake adapter into the base model
Fused model (.safetensors, ~5 GB, 4-bit)
    ↓  Step 2: Dequantize — uncompress weights to full precision
fp16 model (.safetensors, ~16 GB)
    ↓  Step 3: Export to GGUF — convert format + re-compress
GGUF model (.gguf, ~4.6 GB, Q4_K_M)
    ↓  Step 4: Import to Ollama
Ready to use
```

### Step 1: Fuse the Adapter Into the Base Model

**What this does:** During training, the LoRA adapter is a separate file that sits on top of the base model. The base model doesn't change — the adapter just nudges its outputs toward Jacq's voice at runtime. Fusing permanently merges the adapter's changes into the base model's weights, producing a single standalone model.

**Why it's needed:** Ollama (and GGUF) don't understand LoRA adapters. They expect a complete model with all weights baked in. Fusing gives us that.

**Analogy:** The adapter is like an Instagram filter applied live to a photo. Fusing is like saving a new copy of the photo with the filter permanently applied. The result looks identical, but you no longer need the original photo + filter — just the edited version.

**Picking the right checkpoint:** Training saves adapter weights every 100 iterations. The final checkpoint isn't always the best — if validation loss started rising near the end of training, an earlier checkpoint generalized better. Check the training log for the iteration with the lowest validation loss and copy that checkpoint into place before fusing.

```bash
# If using a mid-training checkpoint (e.g., iter 600 had the best val loss):
cp adapters/jacq-v6/0000600_adapters.safetensors adapters/jacq-v6/adapters.safetensors

# Fuse adapter into base model
python -m mlx_lm fuse \
  --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit \
  --adapter-path adapters/jacq-v6 \
  --save-path models/fused/jacq-v6-8b-fused
```

**What you get:** A directory (`models/fused/jacq-v6-8b-fused/`) containing the complete model in MLX's safetensors format. This model already "is" Jacq — no adapter needed. But it's still in MLX's internal 4-bit format, which only MLX can read.

### Step 2: Dequantize to fp16

**What this does:** Converts the model's weights from 4-bit compressed format back to 16-bit full precision (fp16).

**Why it's needed:** The fused model is in MLX's proprietary 4-bit quantization format. The GGUF exporter (next step) can't read MLX's 4-bit format — it needs uncompressed fp16 weights as input so it can apply its own compression scheme. Think of it like this: you can't convert a JPEG directly to WebP — you need to decompress it to raw pixels first, then re-compress in the new format.

**What "dequantize" means:** Quantization is compression — it takes precise numbers (like 0.0023847) and rounds them to fit in fewer bits. Dequantization reverses this, expanding the compressed values back to 16-bit. Some precision was lost during the original 4-bit quantization and can't be recovered, but the expanded values are accurate enough for re-compression in a different format.

**Heads up — this creates a big file:** The 4-bit model is ~5 GB. The fp16 version is ~16 GB. This is temporary — it gets compressed again in the next step.

```bash
python -m mlx_lm convert \
  --hf-path models/fused/jacq-v6-8b-fused \
  --mlx-path models/fused/jacq-v6-8b-fp16 \
  --dtype float16
```

**What you get:** A directory (`models/fused/jacq-v6-8b-fp16/`) containing the full-precision model. This is an intermediate step — you can delete this directory after the GGUF export succeeds.

### Step 3: Export to GGUF

**What this does:** Converts the model from MLX's safetensors format into GGUF (GPT-Generated Unified Format) and re-compresses it using Q4_K_M quantization.

**Why it's needed:** Ollama runs on llama.cpp under the hood, and llama.cpp only reads GGUF files. MLX's safetensors format is great for training on Apple Silicon but can't be used for serving through Ollama.

**What GGUF is:** A single-file format that packages everything Ollama needs — model weights, tokenizer, and configuration — into one `.gguf` file. It's the universal format for local LLM inference.

**What Q4_K_M means:** This is GGUF's quantization method. The "Q4" means 4-bit, and "K_M" is a specific strategy that keeps more precision for important weights while compressing less-important ones more aggressively. It's the best balance of size vs. quality for our use case. The result is ~4.6 GB — similar in size to what we trained on, but in a format Ollama can read.

```bash
python -m mlx_lm gguf \
  --model models/fused/jacq-v6-8b-fp16 \
  --output models/fused/jacq-v6-8b-q4km.gguf \
  --q-type Q4_K_M
```

**What you get:** A single file (`models/fused/jacq-v6-8b-q4km.gguf`, ~4.6 GB) ready for Ollama.

### Step 4: Import to Ollama

**What this does:** Registers the GGUF model with Ollama so you can run it by name.

**Before running this:** Make sure the `Modelfile` in the project root points to the new GGUF path. The `FROM` line should reference the new file:

```
FROM models/fused/jacq-v6-8b-q4km.gguf
```

```bash
ollama create jacq-v6:8b -f Modelfile
```

**What you get:** A model registered in Ollama that you can run with `ollama run jacq-v6:8b` or use through the app.

### Step 5: Evaluate

```bash
python scripts/evaluate.py --model jacq-v6:8b --baseline llama3.1:8b --n 10
```

### Cleanup (Optional)

The intermediate fp16 model is ~16 GB and no longer needed after GGUF export:

```bash
rm -rf models/fused/jacq-v6-8b-fp16
```

Keep the fused 4-bit directory (`jacq-v6-8b-fused`) if you want to use the model directly through MLX without Ollama.

---

## Glossary of Key Terms

### Quantization

**What it is:** A compression technique that reduces the precision of a model's numerical weights. Think of it like reducing the color depth of an image — a 24-bit photo uses millions of colors, but a 256-color version looks nearly identical at a fraction of the file size.

**How it works:** Neural network weights are normally stored as 16-bit or 32-bit floating point numbers (e.g., 0.0023847). Quantization converts these to lower precision formats:

| Format | Bits per weight | 8B model size | Quality |
|--------|----------------|---------------|---------|
| fp32 (full precision) | 32 bits | ~32 GB | Reference |
| fp16 / bf16 (half precision) | 16 bits | ~16 GB | Virtually identical |
| 8-bit (INT8) | 8 bits | ~8 GB | Very close |
| 4-bit (Q4) | 4 bits | ~4-5 GB | Slight degradation, great for most tasks |
| 2-bit | 2 bits | ~2 GB | Noticeable quality loss |

**Why we use it:** Our base model (Llama 3.1 8B) has 8 billion parameters. At full precision, that's 32 GB. At 4-bit quantization, it's ~5 GB — small enough to train on with plenty of room for gradients and activations. The quality difference is minimal for style transfer tasks.

**Trade-off:** Quantized models can't be directly exported to some formats (like GGUF — see below), which is why we dequantize back to fp16 before exporting.

### GGUF (GPT-Generated Unified Format)

**What it is:** A file format for storing language models. It's the standard format used by **llama.cpp** and **Ollama** for inference (running the model to generate text).

**Why it exists:** Different ML frameworks store models differently — PyTorch uses `.pt` files, MLX uses `.safetensors`, etc. GGUF is a universal format designed specifically for efficient CPU/GPU inference. It packages the model weights, tokenizer configuration, and metadata into a single file.

**Why it matters for us:** Our fine-tuned model lives in MLX's `.safetensors` format. To use it with Ollama (our serving layer), we need to convert it to GGUF. The conversion path is: MLX safetensors → dequantize to fp16 → convert to GGUF → re-quantize to Q4_K_M for efficient serving.

**The quantized model problem:** MLX's GGUF exporter can convert fp16 models to GGUF but cannot handle already-quantized models. This is because MLX's internal 4-bit format is different from GGUF's quantization formats (Q4_0, Q4_K_M, etc.). The solution is to dequantize first, then let GGUF tools re-quantize in their own format.

### Fusing (Adapter Fusion)

**What it is:** The process of merging LoRA adapter weights permanently into the base model, creating a standalone model that doesn't need the adapter file anymore.

**Why we do it:** During training, the LoRA adapter is a separate file (~40 MB) that modifies the base model's behavior at runtime. This is efficient for training and experimentation (swap adapters easily), but for production use, we want a single self-contained model.

**How it works technically:** LoRA works by adding small matrices (A and B) to each targeted layer. The adapter modifies a layer's output by computing: `output = original_output + (input × A × B) × scaling_factor`. Fusing performs this multiplication once and adds the result directly to the original weight matrix. After fusing, the model produces identical output but doesn't need the adapter file.

**Analogy:** Think of LoRA adapters like Instagram filters — they're small overlays that change how the image (model output) looks. Fusing is like permanently applying the filter and saving the edited image as a new file.

### LoRA (Low-Rank Adaptation)

**What it is:** A parameter-efficient fine-tuning technique. Instead of modifying all 8 billion parameters in the model (which requires enormous memory), LoRA adds small trainable matrices to specific layers.

**The math (simplified):** A weight matrix in the model might be 4096×4096 (16.7 million values). LoRA replaces training this entire matrix with two smaller matrices: one that's 4096×8 and one that's 8×4096 (65,536 values total — 256x fewer). The "8" is the LoRA rank — a tunable parameter that controls the adapter's capacity.

**QLoRA:** The "Q" means Quantized — we apply LoRA on top of a quantized (4-bit) base model. This dramatically reduces memory: the 4-bit base model uses ~5 GB instead of 16 GB, and we only train ~10.5M parameters instead of 8B.

### Tokens

**What they are:** The atomic units of text that language models work with. Models don't read characters or even whole words — they process **tokens**, which are sub-word pieces typically 3-4 characters long.

**Examples:**
- "Hello world" → `["Hello", " world"]` (2 tokens)
- "unbelievable" → `["un", "believ", "able"]` (3 tokens)
- "Jacqueline" → `["Jac", "quel", "ine"]` (3 tokens)

**Why it matters:** Token count determines memory usage during training, maximum input/output length, and processing speed. Our `max_seq_length: 1024` means each training example can be up to 1024 tokens (~750 words).

### Safetensors

**What it is:** A file format for storing model weights, created by Hugging Face. It's the format MLX uses natively.

**Why not just use PyTorch's format?** Safetensors is faster to load, uses memory mapping (loads only what's needed), and is safer (PyTorch's `.pt` files can contain arbitrary executable code via Python's pickle format, making them a security risk).

### llama.cpp

**What it is:** A C++ implementation of the Llama model inference engine. It's the core technology behind Ollama and many other local AI tools.

**What is C++?** C++ (pronounced "C plus plus") is a programming language known for running very fast because it compiles directly to machine code (unlike Python, which is interpreted). The `.cpp` file extension denotes C++ source code. ML frameworks like PyTorch and MLX are written in Python for ease of use, but their performance-critical parts (and llama.cpp entirely) are written in C/C++ for speed.

**Why it matters:** llama.cpp made it possible to run large language models on consumer hardware (laptops, phones) by implementing highly optimized inference code. Ollama is essentially a user-friendly wrapper around llama.cpp — when you run `ollama run jacq:8b`, it's llama.cpp doing the actual text generation under the hood.

### Inference vs. Training

**Training** is the process of adjusting model weights to learn from data. It requires computing gradients (how to change each weight) and storing intermediate values, which uses much more memory than just running the model.

**Inference** is using the trained model to generate text. It only needs to run the model forward (no gradients, no weight updates), so it's faster and uses less memory.

**In our project:**
- **Training** happens via MLX (`mlx_lm.lora`) — ~6.4 GB, ~549 tokens/sec
- **Inference** happens via Ollama/llama.cpp or MLX (`mlx_lm.generate`) — ~4.6 GB, ~129 tokens/sec for generation

### Transformer Layers

**What they are:** The building blocks of modern language models. Llama 3.1 8B has 32 transformer layers stacked on top of each other. Each layer contains attention mechanisms (deciding which words to focus on) and feed-forward networks (processing the information).

**Why we only train 16 layers:** Lower layers learn basic language features (grammar, common phrases). Upper layers learn higher-level patterns (style, tone, content decisions). For voice/style transfer, we only need to modify the upper 16 layers — the lower layers' language fundamentals are already good.

### Gradient Checkpointing

**What it is:** A memory-saving technique for training. During the forward pass, the model computes intermediate values at every layer. Normally these are all stored in memory for the backward pass. Gradient checkpointing discards most of them and recomputes them as needed.

**The trade-off:** Uses ~2x more compute time but dramatically less memory. In our case, it dropped peak memory from 62 GB to 6.4 GB — making training possible without crashing the GPU.

### Epochs

**What it is:** One complete pass through the entire training dataset. With 691 training examples and 600 iterations (batch_size 1), we do slightly less than 1 epoch — the model sees most but not all of the training data once.

**Why ~1 epoch is our sweet spot:** For style transfer fine-tuning, 1-3 epochs is typical. Too few epochs and the model hasn't learned enough. Too many and it starts memorizing specific training examples instead of learning general patterns (overfitting).

### Overfitting

**What it is:** When a model memorizes the training data instead of learning general patterns from it. An overfit model gets really good at repeating back what it's seen, but bad at generating new content.

**A simple analogy:** Imagine studying for an exam by memorizing every practice question word-for-word. If the exam has the exact same questions, you ace it. But if the questions are rephrased even slightly, you're lost — because you memorized answers instead of understanding the material. That's overfitting.

**How it shows up in this project:** An overfit Jacq model would parrot back exact sentences and paragraphs from her blog posts and books instead of writing *new* content in her voice. You'd ask it to write about morning routines and it would spit out a nearly verbatim copy of a training post, rather than generating something fresh that sounds like her. The writing might look perfect at first glance — because it literally is her writing — but it can't handle new topics, new angles, or prompts that don't closely match something in the training data.

**How to spot it — the train/val gap:** During training, we measure two loss numbers:

- **Train loss** — How well the model predicts the data it's actively learning from. This always goes down over time.
- **Val loss (validation loss)** — How well the model predicts held-out data it has *never* seen during training. This is the honest test.

The **gap** between these two numbers is the overfitting signal:

| Train Loss | Val Loss | Gap | What It Means |
|-----------|---------|-----|---------------|
| 1.30 | 1.24 | 0.06 | Healthy — model generalizes well to new text |
| 1.30 | 1.45 | 0.15 | Mild concern — keep watching |
| 1.10 | 1.80 | 0.70 | Overfitting — model is memorizing, not learning |

When the model is learning genuine patterns (sentence rhythm, word choice tendencies, tone), both numbers drop together and the gap stays small. When it starts memorizing specific training examples, train loss keeps dropping (it's getting better at the training data) but val loss stops dropping or starts *rising* (it's getting worse at new text). That widening gap is the red flag.

**Why 2 epochs is our sweet spot:** We've found that 2 full passes through the training data gives the model enough exposure to learn Jacq's voice patterns without tipping into memorization. At 3 epochs (v2), the model over-smoothed — it averaged out Jacq's distinctive stylistic features into a blander version. At 2 epochs (v4), the train/val gap stayed at 0.047, which is excellent.

**What we do about it:** We save checkpoints every 100 iterations during training. If later checkpoints show a widening gap, we can roll back to an earlier checkpoint that generalized better — we don't have to use the final one.
