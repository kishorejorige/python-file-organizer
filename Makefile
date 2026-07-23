.PHONY: help install-dev build pyinstaller dist release lint format-check test security-scan docker-build docker-test

help:
	@echo "Makefile targets:"
	@echo "  make install-dev   # Install build/dev tools via uv"
	@echo "  make lint          # Run ruff check"
	@echo "  make format-check  # Run ruff format --check"
	@echo "  make test          # Run pytest"
	@echo "  make security-scan # Run bandit and pip-audit security scans"
	@echo "  make build         # Build sdist and wheel using uv build"
	@echo "  make pyinstaller   # Build a single-file executable using PyInstaller via uv run"
	@echo "  make dist          # Build both wheel/sdist and pyinstaller binary"
	@echo "  make release       # Run ./release.sh (requires gh CLI)"
	@echo "  make docker-build  # Build local Docker image"
	@echo "  make docker-test   # Run doctor diagnostics inside Docker"

install-dev:
	uv sync --dev

lint:
	uv run ruff check .

format-check:
	uv run ruff format --check .

test:
	uv run pytest

security-scan:
	uv run bandit -r organizer
	uv run pip-audit

build:
	uv build

pyinstaller:
	uv run python -c "from pathlib import Path; Path('dist/pyinstaller').mkdir(parents=True, exist_ok=True)"
	uv run pyinstaller --clean -y --distpath dist/pyinstaller file-organizer.spec

dist: build pyinstaller

release: dist
	./release.sh

docker-build:
	docker build -t python-file-organizer:local .

docker-test:
	docker run --rm python-file-organizer:local

