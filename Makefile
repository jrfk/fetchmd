# Python モジュール実行のショートカット
PY=python -m

# デフォルトターゲット (make とだけ打った場合)
.DEFAULT_GOAL := help

# --- Development Setup ---

install: ## Install dependencies using uv
	uv pip install -e ".[all,dev]"

# --- Testing & Linting ---

test: ## Run tests using pytest
	pytest -q tests/

lint: ## Run ruff linter
	ruff check .

format: ## Auto-format code with ruff
	ruff format .

# --- Running the Application ---

# make run URL="https://example.com https://another.com" OUT=./output
run: ## Run fetchmd CLI with specified URL(s)
ifndef URL
	$(error URL is not set. Usage: make run URL="<url1> <url2>...")
endif
	fetchmd $(URL) --out $(or $(OUT),out)

# --- Help ---

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.PHONY: install test lint format run help