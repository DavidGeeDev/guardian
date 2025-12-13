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

## Plugin loading (entry points)

Model Guardian supports registering adapters without forking via Python package entry points:

- `model_guardian.models`
- `model_guardian.uncertainty_adapters`
- `model_guardian.drift_adapters`
- `model_guardian.policies`
- `model_guardian.telemetry_sinks`

Phase 0 ships built-ins (MAPIE, Alibi KSDrift, JSONL sink) pre-registered in `pyproject.toml`.

Example (build a guardian from entry points):

```python
from model_guardian import PluginSpec, build_guardian

guardian = build_guardian(
    model=PluginSpec(group="model_guardian.models", entrypoint="mapie"),
    uncertainty=PluginSpec(group="model_guardian.uncertainty_adapters", entrypoint="mapie"),
    telemetry=PluginSpec(group="model_guardian.telemetry_sinks", entrypoint="jsonl"),
    telemetry_kwargs={"path": "logs/guardian.jsonl"},
)
```

## Drift modes

`GuardianConfig.drift_mode` controls drift behavior:

- `off`: don't run drift checks
- `shadow` (default): run drift checks asynchronously and log them, but do **not** let them affect the policy
- `enforce`: include drift signals in policy inputs

Env-based settings are available via `model_guardian.schemas.GuardianSettings` with prefix `MODEL_GUARDIAN_`.

## Raw artifact immutability

Phase 0 deep-freezes `Prediction.raw` (recursively) so adapters can't accidentally mutate audit artifacts.

> Note: for arrays, we defensively copy and mark as read-only when possible.

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
