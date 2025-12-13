# Reproducible Builds & Lockfiles

This repo uses **pyproject.toml** as the single source of truth for declared dependencies.
For fully reproducible installs (exact versions + hashes), commit lockfiles generated from the pyproject.

## Option A (recommended): uv

1) Install:

```bash
pip install uv
```

2) Generate lockfiles:

```bash
make lock-uv
```

This produces:
- `requirements/base.lock`  (runtime)
- `requirements/dev.lock`   (runtime + dev extras)

3) Install from lockfile (hash-verified):

```bash
pip install --require-hashes -r requirements/base.lock
pip install -e .
```

## Option B: pip-tools

1) Install:

```bash
pip install pip-tools
```

2) Generate lockfiles:

```bash
make lock-piptools
```

3) Install from lockfile:

```bash
pip install --require-hashes -r requirements/dev.lock
pip install -e .
```

## CI guidance

The GitHub Actions workflow runs:
- `make test` (compileall + pytest)
- `make run-example` (Phase 0 end-to-end smoke)
- `make lint` (ruff)
- `make typecheck` (mypy, advisory)
