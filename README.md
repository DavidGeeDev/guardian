# Model Guardian — Phase 0 (Model-Agnostic Core)

Phase 0 is an **in-process (decorator/middleware) wrapper** around a model's `predict()` call that:
- adds **Humility** via post-hoc uncertainty quantification (MAPIE in Phase 0),
- adds **Safety** via non-blocking drift signals (Alibi-Detect patterns),
- produces a **typed** `GuardianResponse` that either returns the prediction or refuses safely.

## Quickstart (Hello World)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python examples/sklearn_mapie_hello_world.py
```

## Run the example API

```bash
uvicorn model_guardian.api.app:app --reload
```

Then POST:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H 'content-type: application/json' \
  -d '{"features":[5.1,3.5,1.4,0.2]}'
```

## What you get back

A `GuardianResponse` including:
- `prediction` (if allowed),
- `uncertainty` (aleatoric + epistemic),
- `decision` (ALLOW/ABSTAIN/DEGRADE/BLOCK),
- `signals` (drift + any extra providers),
- `failure` (if refused) and a traceable rationale.

## Repo layout

- `model_guardian/interfaces/` — stable kernel ABIs
- `model_guardian/schemas/` — Pydantic V2 data contracts
- `model_guardian/core/` — orchestration + default policy + telemetry
- `model_guardian/implementations/` — MAPIE + Alibi-Detect adapters
- `model_guardian/api/` — FastAPI wrapper for demo use
- `examples/` — sklearn + MAPIE "Hello World"
- `tests/` — sanity tests for async flow and schemas
