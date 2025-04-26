# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands
- Install dependencies: `make install` (uses uv)
- Run tests: `make test` (uses pytest)
- Run single test: `pytest tests/path_to_test.py::test_function_name`
- Run the app: `make run URL="https://example.com"` or `python -m fetchmd URL [OPTIONS]`
- Lint: `make lint` (uses ruff)
- Format: `make format` (uses ruff format)

## Code Style Guidelines
- Python 3.10+ compatible code
- Use type hints for all function parameters and return values
- Follow PEP 8 for formatting with 100 character line length
- Imports: standard library first, third-party second, local imports last
- Async/await for I/O operations (httpx, aiofiles)
- Use descriptive variable names in snake_case
- Function/method names: snake_case
- Class names: PascalCase
- Error handling: prefer explicit try/except blocks
- Document functions with docstrings using triple quotes
- Organize code into logical modules in the fetchmd package
- CLI interface uses typer library
- Use YAML front-matter in generated markdown files
- Follow commit message format: feat/fix/docs/chore/test

## CI Workflow
- GitHub Actions CI runs on each push and pull request
- Lint job validates code style with ruff
- Test job runs pytest and a basic functional test with example.com