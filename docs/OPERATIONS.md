# Operations Guide

Everything needed to run, configure, and maintain the writing assistant. Covers environment setup, authentication, model management, and all operational commands.

---

## Environment

### Hardware
- Mac Studio M3 Ultra, 96 GB unified memory
- MLX uses Apple Silicon GPU natively (no CUDA)

### Python
```bash
# Python 3.12.8 via pyenv (ML libs require 3.12, not 3.14)
pyenv install 3.12.8
pyenv local 3.12.8

# Virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Key Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| mlx-lm | 0.30.7 | Fine-tuning on Apple Silicon |
| ollama (CLI) | 0.17.4 | Model serving |
| next.js | 15 | Web UI (frontend) |
| fastapi | 0.115+ | API server (backend) |
| chromadb | 1.5.2 | Vector database (RAG) |
| httpx | — | HTTP client (LinkedIn, scraping) |
| beautifulsoup4 | — | HTML parsing |
| lxml | — | HTML parser backend |

---

## Ollama

### Design
Ollama runs **on-demand only** — NOT as a persistent service. The `OllamaManager` class in `app/assistant.py` starts Ollama when needed and stops it when done to conserve memory.

### Commands
```bash
# Start manually (for testing)
ollama serve

# List installed models
ollama list

# Run a model interactively
ollama run jacq-v6:8b

# Import/update a model from Modelfile
ollama create jacq-v6:8b -f Modelfile

# Pull a base model
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### Models in Use
| Model | Size | Purpose |
|-------|------|---------|
| jacq-v6:8b | 4.6 GB | Production fine-tuned model |
| llama3.1:8b | 4.6 GB | Base model (for comparison) |
| nomic-embed-text | 274 MB | Embeddings for RAG + evaluation |

### Model Files
- GGUF: `models/fused/jacq-v6-8b-q4km.gguf`
- Modelfile: `Modelfile` (project root — contains FROM path + system prompt + parameters)
- Ollama storage: `~/.ollama/models/`

---

## Web UI (Next.js + FastAPI)

### Starting the App
```bash
# Start both servers (FastAPI on 8000, Next.js on 7860)
make dev

# Or start individually
make dev-api    # FastAPI only
make dev-web    # Next.js only

# Stop all servers
make stop
```

Opens at **https://localhost:7860** (self-signed SSL cert).

### Features
- **Writing types**: Blog Post, Email (Outbound), Email Reply, Copywriting, LinkedIn Post, Freeform
- **WYSIWYG editor**: Rich text editing with Tiptap (bold, italic, underline, headings, lists)
- **Model settings**: Model dropdown, temperature slider, max tokens, RAG toggle (with tooltips)
- **LinkedIn multi-post**: Select blog from GA4 → generate N posts → edit/schedule/post each
- **Scheduling**: Pick date/time per post, manage scheduled posts table
- **Email Reply**: Paste received email → generates reply → Send Email button
- **Feedback**: Save Edits captures original + edited pairs for future training

### Temperature Defaults
| Task | Default | Notes |
|------|---------|-------|
| LinkedIn | 0.6 | Sweet spot — warm voice, controlled output |
| All others | 0.7 | Slightly more creative for longer content |

---

## CLI

```bash
# Blog post
python app/cli.py blog "Write about morning routines"

# Email
python app/cli.py email "Follow up on the coaching proposal" \
  --recipient "Sarah" --purpose "Follow up" --email-type professional

# LinkedIn (paste blog URL as topic)
python app/cli.py linkedin "https://theintuitivewritingschool.com/blog/..."

# Freeform
python app/cli.py freeform "Write a thank you note"

# With options
python app/cli.py blog "topic" --model jacq-v6:8b --temperature 0.7 --max-tokens 2048 --rag
```

---

## Authentication & Credentials

All credentials live in `credentials/` (gitignored).

### LinkedIn

**Credential files:**
- `credentials/linkedin_credentials.json` — App client ID and secret
- `credentials/linkedin_token.json` — Access token, expiry, person ID

**Initial setup:**
1. Create a LinkedIn app at https://developer.linkedin.com
2. Add the **"Share on LinkedIn"** product (grants `w_member_social` scope)
3. Add the **"Sign In with LinkedIn using OpenID Connect"** product (grants `openid` scope)
4. Set redirect URI to `http://localhost:8888/callback`
5. Wait for app verification (may require a Company Page)
6. Save credentials:
   ```json
   // credentials/linkedin_credentials.json
   {"client_id": "YOUR_CLIENT_ID", "client_secret": "YOUR_CLIENT_SECRET"}
   ```
7. Run the auth flow:
   ```bash
   source .venv/bin/activate
   python scripts/linkedin_auth.py
   ```
   - Opens browser for OAuth consent
   - Catches callback on `localhost:8888`
   - Saves token + person ID to `credentials/linkedin_token.json`

**Token format:**
```json
{
  "access_token": "AQW...",
  "expires_at": 1777590083,
  "person_id": "5B_UUPUea6"
}
```

**Re-authentication:**
```bash
# Token expires ~60 days after issuance
python scripts/linkedin_auth.py
```

**Alternative (portal-generated token):**
If the auth script fails, generate a token via the LinkedIn Developer Portal:
1. Go to your app → OAuth 2.0 tools
2. Select scopes: `openid`, `w_member_social`
3. Generate token
4. Get person ID from `/v2/userinfo` endpoint:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.linkedin.com/v2/userinfo
   # Use the "sub" field as person_id
   ```
5. Save to `credentials/linkedin_token.json`

**API details:**
- API version header: `LinkedIn-Version: 202507`
- Post endpoint: `POST https://api.linkedin.com/rest/posts`
- Author format: `urn:li:person:{person_id}` (person_id is the `sub` from OpenID)
- Required scopes: `openid` + `w_member_social`

### Gmail

**Credential files:**
- `credentials/gmail_credentials.json` — OAuth2 client credentials
- `credentials/gmail_token.json` — Access/refresh token

**Setup:**
1. Create a Google Cloud project
2. Enable the Gmail API
3. Create OAuth2 credentials (Desktop app type)
4. Download credentials JSON to `credentials/gmail_credentials.json`
5. Run the Gmail auth flow (first use triggers browser consent)

### Google Analytics

**Credential file:**
- `credentials/ga_service_account.json` — Service account key

**Setup:**
1. Create a service account in Google Cloud
2. Enable the Google Analytics Data API
3. Download the service account key JSON
4. Add the service account email as a Viewer on the GA4 property
5. Property ID: `359976766`

**Usage:**
```bash
python scripts/analytics.py
```

---

## Training Pipeline

### Full Training Run
```bash
source .venv/bin/activate

# 1. Build/update training data
python scripts/build_training_data.py

# 2. Split into train/valid/test
python scripts/split_dataset.py

# 3. Train LoRA adapter
python -m mlx_lm.lora --config configs/lora_config.yaml

# 4. Check val loss curve — find the iteration with lowest val loss
# Look at training output for "Val loss" entries every 50 steps

# 5. Copy best checkpoint into place
cp adapters/jacq-v6/0000600_adapters.safetensors adapters/jacq-v6/adapters.safetensors
```

### Training Config: `configs/lora_config.yaml`
```yaml
model: "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
train: true
data: "data/training"
lora_layers: 16
lora_rank: 16
lora_alpha: 32
learning_rate: 1.0e-5
batch_size: 1
max_seq_length: 2048
iters: 916           # 2 epochs on current dataset
adapter_path: "adapters/jacq-v6"
save_every: 100
val_batches: 25
steps_per_eval: 50
grad_checkpoint: true
```

### Key Training Parameters
| Parameter | Value | Why |
|-----------|-------|-----|
| lora_rank | 16 | Enough capacity for voice cloning without overfitting |
| lora_alpha | 32 | 2x rank — standard scaling |
| epochs | 2 | Sweet spot — 1 undertrained, 3 over-smoothed |
| batch_size | 1 | Memory constraint; noisy gradient actually helps voice capture |
| max_seq_length | 2048 | Full blog post length |
| grad_checkpoint | true | Drops memory from 62 GB to ~8 GB |

---

## Model Export Pipeline

After training, convert the LoRA adapter to a GGUF model for Ollama.

```bash
source .venv/bin/activate

# 1. Fuse adapter into base model
python -m mlx_lm fuse \
  --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit \
  --adapter-path adapters/jacq-v6 \
  --save-path models/fused/jacq-v6-8b-fused

# 2. Dequantize to fp16 (intermediate step)
python -m mlx_lm convert \
  --hf-path models/fused/jacq-v6-8b-fused \
  --mlx-path models/fused/jacq-v6-8b-fp16 \
  --dtype float16

# 3. Export to GGUF with Q4_K_M quantization
python -m mlx_lm gguf \
  --model models/fused/jacq-v6-8b-fp16 \
  --output models/fused/jacq-v6-8b-q4km.gguf \
  --q-type Q4_K_M

# 4. Import into Ollama
ollama create jacq-v6:8b -f Modelfile

# 5. Cleanup (optional — delete 16 GB intermediate fp16 model)
rm -rf models/fused/jacq-v6-8b-fp16
```

**Pipeline summary:**
```
MLX 4-bit LoRA adapters (~50 MB)
    → fuse into base model (4-bit safetensors, ~5 GB)
    → dequantize to fp16 (safetensors, ~16 GB)
    → convert to GGUF Q4_K_M (.gguf, ~4.6 GB)
    → import to Ollama
```

---

## Evaluation

```bash
source .venv/bin/activate

# Full evaluation (perplexity + generation + metrics)
python scripts/evaluate.py --model jacq-v6:8b --baseline llama3.1:8b --n 10

# With RAG (for testing — NOT recommended for voice)
python scripts/evaluate.py --model jacq-v6:8b --baseline llama3.1:8b --n 10 --rag

# Style analysis on generated output
python scripts/analyze_style.py path/to/output.txt
```

### Evaluation Metrics
1. **Perplexity** (MLX) — does the model predict Jacq's words? Lower = better
2. **Embedding similarity** (nomic-embed-text) — does output match her style-space? Higher = better (target >0.70)
3. **Failure mode detection** — buzzword count (<5), dash density (7-14/1k), fragment rate (~15%)

---

## Data Pipeline

### Scraping New Blog Posts
```bash
# Scrape new posts from theintuitivewritingschool.com
python scripts/scrape_blog.py

# Extract and clean
python scripts/extract_docx.py
python scripts/clean_text.py
python scripts/analyze_style.py
```

### Building Training Data
```bash
# Build training examples with buzzword filter
python scripts/build_training_data.py

# Build style exemplars (top 20 Jacq-ness scored posts + 15 hand-crafted)
python scripts/build_exemplars.py

# Split into train/valid/test
python scripts/split_dataset.py
```

### Data Locations
| Path | Contents |
|------|----------|
| `data/raw/books/` | Source book files |
| `data/raw/blog/` | Source blog post files |
| `data/cleaned/` | Cleaned text files |
| `data/training/` | JSONL training data |
| `data/training/train.jsonl` | Training split (~458 examples) |
| `data/training/valid.jsonl` | Validation split (~57 examples) |
| `data/training/test.jsonl` | Test split (~58 examples) |
| `data/training/exemplars.jsonl` | Style exemplars for training |

---

## RAG (ChromaDB)

### When to Use RAG
- **YES**: Factual retrieval — "What did Jacq write about Sedona?"
- **NO**: Voice generation — blog posts, LinkedIn posts, emails (RAG hurts voice quality)

### Commands
```bash
# Ingest content into ChromaDB
python rag/ingest.py

# ChromaDB data stored in: chroma_db/ (project root)
```

### Default: OFF
- `app/assistant.py`: `use_rag=False`
- `scripts/evaluate.py`: `--rag` flag to opt in
- RAG infrastructure stays in place for factual retrieval use cases

---

## Feedback & Training Data Collection

### How it works
Every time content is generated and saved/sent/posted from the web UI, a record is saved to `data/feedback/feedback.jsonl` containing:
- Task type, model, temperature
- Full prompt sent to the model
- Original model output
- Edited output (after user modifications)
- Whether it was edited (`was_edited: true/false`)
- Whether it was sent/posted (`was_sent: true/false`)

### Using Feedback for Training
```bash
# Analyze feedback patterns
python scripts/eval_feedback.py
```

These original→edited pairs can be used to improve future model versions by training on the edited (human-corrected) outputs.

---

## File Structure

```
digital-twin/
├── app/
│   ├── assistant.py         # Core generation logic, OllamaManager
│   ├── cli.py               # Command-line interface
│   ├── (web.py removed)      # Replaced by web/ + api/
│   ├── ollama_client.py      # Ollama HTTP client
│   ├── gmail_client.py       # Gmail API client
│   ├── linkedin_client.py    # LinkedIn API client
│   └── feedback_store.py     # JSONL feedback storage
├── configs/
│   └── lora_config.yaml      # Training configuration
├── credentials/              # gitignored
│   ├── gmail_credentials.json
│   ├── gmail_token.json
│   ├── ga_service_account.json
│   ├── linkedin_credentials.json
│   └── linkedin_token.json
├── adapters/
│   ├── jacq-v1/              # v1 LoRA checkpoints
│   ├── jacq-v4/              # v4 LoRA checkpoints
│   ├── jacq-v5/              # v5 LoRA checkpoints
│   └── jacq-v6/              # v6 LoRA checkpoints (production)
├── models/fused/
│   └── jacq-v6-8b-q4km.gguf # Production GGUF model
├── prompts/
│   ├── system_prompt.txt     # Main system prompt (baked into Modelfile)
│   ├── blog.txt              # Blog post template
│   ├── email.txt             # Email template
│   ├── email_reply.txt       # Email reply template
│   ├── copywriting.txt       # Copywriting template
│   └── linkedin.txt          # LinkedIn post template
├── scripts/                  # Data pipeline, training, evaluation
├── rag/                      # RAG pipeline (retriever, ingestion)
├── data/                     # Training data, feedback
├── docs/                     # Project documentation
│   ├── FEATURES.md           # Feature ideas and roadmap
│   ├── TRAINING_GUIDE.md     # Fine-tuning guide
│   ├── ML_CONCEPTS.md        # ML/AI concepts reference
│   └── OPERATIONS.md         # This file
├── Modelfile                 # Ollama model definition
├── PROJECT_LOG.md            # Training history and decisions
└── README.md                 # Quick start
```
