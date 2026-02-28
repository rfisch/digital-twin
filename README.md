# Digital Twin — Jacq's Writing Assistant

A fine-tuned writing assistant that emulates Jacq's writing voice for blog posts, emails, and copywriting.

## Architecture

| Layer | Tool | Purpose |
|-------|------|---------|
| Fine-tuning | MLX (mlx-lm) | Native Apple Silicon training |
| Inference | Ollama | Model serving and API |
| RAG | ChromaDB + Ollama | Content grounding with vector search |

## Quick Start

```bash
# Activate the environment
source .venv/bin/activate

# Run the CLI
python app/cli.py blog "Write about morning routines"

# Run the web UI
python app/web.py
```

## Data Pipeline

```bash
# 1. Place raw files in data/raw/books/ and data/raw/blog/
# 2. Extract text
python scripts/extract_pdf.py
python scripts/extract_docx.py
python scripts/extract_blog.py

# 3. Clean and analyze
python scripts/clean_text.py
python scripts/analyze_style.py

# 4. Build training data
python scripts/build_training_data.py

# 5. Split into train/valid/test
python scripts/split_dataset.py
```

## Fine-Tuning

```bash
# Train LoRA adapter
python -m mlx_lm.lora --config configs/lora_config.yaml

# Test adapter
python -m mlx_lm.generate --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit \
    --adapter-path adapters/jacq-v1 \
    --prompt "Write a blog post about..."

# Fuse and export
python -m mlx_lm.fuse --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit \
    --adapter-path adapters/jacq-v1 \
    --export-gguf

# Import into Ollama
ollama create jacq:8b -f Modelfile
```

## Project Structure

See `PROJECT_LOG.md` for detailed decisions, research notes, and progress tracking.
