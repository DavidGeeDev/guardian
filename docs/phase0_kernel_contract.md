## Scope (Phase 0)

### Goals (we will build)
- A model-agnostic in-process wrapper (Decorator/Middleware pattern).
- Humility: post-hoc uncertainty signal(s) using MAPIE.
- Awareness scaffolding: drift adapter interface + placeholder implementation that can run non-blocking.
- A policy engine that can allow / degrade / abstain / block based on signals.
- Unified logging schema with trace IDs and auditable outputs.

### Non-goals (we will NOT build in Phase 0)
- Full drift enforcement (drift will run in shadow mode/log-only).
- NannyML-like post-deployment analytics and root cause tooling.
- Multiple uncertainty engines (TorchCP support is future; Phase 0 uses MAPIE).
- Complex per-domain policies (start with a basic threshold policy only).
