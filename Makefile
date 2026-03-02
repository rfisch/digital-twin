.PHONY: help dev dev-api dev-web storybook stop \
       test test-api test-web test-web-watch \
       install install-api install-web \
       lint lint-web \
       scrape-blog extract-blog build-data build-exemplars split-data analyze-style data-pipeline \
       train \
       export-model export-model-v6 \
       eval-feedback evaluate evaluate-quick \
       post-scheduled cron-install cron-remove \
       setup fresh

.DEFAULT_GOAL := help

help: ## Show all available commands
	@echo ""
	@echo "  Jacq's Digital Twin — Makefile Commands"
	@echo "  ──────────────────────────────────────────"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ─── Application Management ──────────────────────────────────────────

dev: ## Start FastAPI + Next.js dev servers
	bash scripts/dev.sh

dev-api: ## Start FastAPI server only (port 8000)
	source .venv/bin/activate && uvicorn api.main:app --reload --port 8000

dev-web: ## Start Next.js server only (port 7860)
	cd web && npm run dev

storybook: ## Start Storybook (port 6006)
	cd web && npm run storybook

stop: ## Kill all dev servers (ports 8000, 7860)
	@echo "Stopping dev servers..."
	@-lsof -ti:8000 | xargs kill 2>/dev/null; true
	@-lsof -ti:7860 | xargs kill 2>/dev/null; true
	@echo "Done."

# ─── Testing ─────────────────────────────────────────────────────────

test: test-api test-web ## Run all tests (API + frontend)

test-api: ## Run FastAPI tests (pytest)
	source .venv/bin/activate && pytest api/

test-web: ## Run frontend unit tests (vitest)
	cd web && npx vitest run

test-web-watch: ## Run frontend tests in watch mode
	cd web && npx vitest

# ─── Dependencies ────────────────────────────────────────────────────

install: install-api install-web ## Install all dependencies

install-api: ## Install Python dependencies
	source .venv/bin/activate && pip install -r requirements.txt

install-web: ## Install Node.js dependencies
	cd web && npm install

# ─── Linting ─────────────────────────────────────────────────────────

lint: lint-web ## Run all linters

lint-web: ## Lint frontend (ESLint + TypeScript)
	cd web && npx next lint && npx tsc --noEmit

# ─── Data Pipeline ───────────────────────────────────────────────────

scrape-blog: ## Scrape blog posts from Squarespace + Substack
	source .venv/bin/activate && python scripts/scrape_blog.py

extract-blog: ## Extract text from raw HTML/XML
	source .venv/bin/activate && python scripts/extract_blog.py

build-data: ## Build instruction-tuning JSONL
	source .venv/bin/activate && python scripts/build_training_data.py

build-exemplars: ## Build style exemplars for training
	source .venv/bin/activate && python scripts/build_exemplars.py

split-data: ## Split dataset 80/10/10 train/valid/test
	source .venv/bin/activate && python scripts/split_dataset.py

analyze-style: ## Analyze writing style metrics
	source .venv/bin/activate && python scripts/analyze_style.py

data-pipeline: scrape-blog extract-blog build-data build-exemplars split-data ## Run full data pipeline

# ─── Training ────────────────────────────────────────────────────────

train: ## Train LoRA adapter (MLX)
	source .venv/bin/activate && python -m mlx_lm.lora --config configs/lora_config.yaml

# ─── Model Export ────────────────────────────────────────────────────

export-model: ## Fuse adapter + export GGUF + import to Ollama
	source .venv/bin/activate && python scripts/export_model.py

export-model-v6: ## Export jacq-v6:8b specifically
	source .venv/bin/activate && python scripts/export_model.py --adapter-path adapters/jacq-v6 --name jacq-v6:8b

# ─── Evaluation ──────────────────────────────────────────────────────

eval-feedback: ## Assess feedback pairs — recommend if ready to retrain
	source .venv/bin/activate && python scripts/eval_feedback.py

evaluate: ## Full evaluation (perplexity + embedding + failure modes)
	source .venv/bin/activate && python scripts/evaluate.py

evaluate-quick: ## Quick evaluation (skip perplexity + failure modes)
	source .venv/bin/activate && python scripts/evaluate.py --skip-perplexity --skip-failure-modes

# ─── Scheduling ──────────────────────────────────────────────────────

post-scheduled: ## Post any due scheduled LinkedIn posts
	source .venv/bin/activate && python scripts/post_scheduled.py

cron-install: ## Install crontab entry (every 15 min)
	@echo "Installing crontab for post_scheduled (every 15 min)..."
	(crontab -l 2>/dev/null | grep -v 'post_scheduled'; echo "*/15 * * * * cd $(pwd) && source .venv/bin/activate && python scripts/post_scheduled.py >> logs/cron.log 2>&1") | crontab -
	@echo "Done. Verify with: crontab -l"

cron-remove: ## Remove post_scheduled crontab entry
	@echo "Removing post_scheduled crontab entry..."
	crontab -l 2>/dev/null | grep -v 'post_scheduled' | crontab -
	@echo "Done."

# ─── Compound ────────────────────────────────────────────────────────

setup: install ## Full setup (install all deps)

fresh: scrape-blog build-data split-data train export-model evaluate ## Clean rebuild: data → train → export → eval
