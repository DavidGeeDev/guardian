.PHONY: help install install-dev lock-uv lock-piptools test lint typecheck run-example api clean

PY ?= python
PIP ?= pip

help:
	@echo "Targets:"
	@echo "  install         Install package (editable)"
	@echo "  install-dev     Install package with dev extras"
	@echo "  lock-uv         Generate requirements/base.lock and requirements/dev.lock via uv (recommended)"
	@echo "  lock-piptools   Generate requirements/*.lock via pip-tools"
	@echo "  test            Compile + run pytest"
	@echo "  lint            Run ruff (requires dev extras)"
	@echo "  typecheck       Run mypy (requires dev extras)"
	@echo "  run-example     Run Phase 0 hello world example"
	@echo "  api             Run FastAPI app via uvicorn"
	@echo "  clean           Remove caches/build artifacts"

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

lock-uv:
	@./scripts/lock_uv.sh

lock-piptools:
	@./scripts/lock_piptools.sh

test:
	$(PY) -m compileall -q model_guardian
	pytest -q

lint:
	ruff check model_guardian tests examples

typecheck:
	mypy model_guardian

run-example:
	$(PY) examples/sklearn_mapie_hello_world.py

api:
	uvicorn model_guardian.api.app:app --host 0.0.0.0 --port 8000

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache __pycache__ */__pycache__ dist build *.egg-info
