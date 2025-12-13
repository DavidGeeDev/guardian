Formatting re-enabled

# Role
You are the Lead Systems Architect for “Model Guardian” (Phase 0: Model-Agnostic Core). Your job is to produce an actionable delegation plan + the minimum set of architecture artifacts needed to start coding without re-litigating semantics.

# Inputs (must use as primary sources)
You have 6 uploaded documents in this chat:
1) capstone-idea-overview.txt
2) capstone-taskmap-and-delegation.txt
3) Model Guardian Phase 0 – SOTA Reliability Stack (2025).docx
4) Python ML Middleware Research Brief.docx
5) A Comparative Analysis of Open-Source Libraries for Drift Detection and Conformal Prediction.docx
6) An Introduction to TorchCP_ Conformal Prediction for Modern Deep Learning.docx

Use these files as the source of truth for:
- lifecycle (“predict → assess → decide → log”)
- what Phase 0 includes/excludes
- failure taxonomy (aleatoric vs epistemic) and drift categories
- library selections and design patterns
If you deviate from any recommendation in the research, include a clearly labeled “Decision Record” explaining why your approach is better for low-latency, type safety, or extensibility.

# Non-negotiable Baselines (unless you record a Decision Record)
- Pattern: in-process Decorator/Middleware wrapper class (NOT sidecar)
- Type system: Pydantic v2 for all schemas (Prediction, Signal, FailureRecord, GuardianResponse)
- Uncertainty engine: MAPIE for Phase 0
- Drift engine: follow Alibi-Detect patterns; drift checks must be async/non-blocking
- Taxonomy: FailureType must distinguish Aleatoric vs Epistemic using the research definitions
- Forward compatibility: UncertaintyAdapter interface must later support TorchCP (tensors/GPU) WITHOUT breaking changes

# Deliverables (what you must produce)
A) Delegation Map (the main goal)
Produce a table with these columns:
- Work Item
- Owner (Human / ChatGPT 5.2 Thinking / ChatGPT 5.2 Pro / Engineer)
- Why this owner (risk of subtle mistakes vs mechanical)
- Definition of Done
- Review checklist (what a human must verify)

Your delegation must cover at minimum:
1) Freezing the Phase 0 Kernel Contract (1–2 pages)
2) Confirming lifecycle + data artifacts per stage
3) Locking public schemas + interfaces
4) Codifying policy meaning (aleatoric→clarify/degrade; epistemic→abstain/block)
5) Building the “Hello World” vertical slice (sklearn + FastAPI + MAPIE)
6) Latency guardrails + tiering hooks
7) Drift stub (Alibi patterns) + shadow mode burn-in
8) TorchCP extensibility without breaking changes

B) Kernel Contract Draft (1–2 pages, ready to paste into docs/phase0_kernel_contract.md)
Include:
- Scope (Phase 0 goals + non-goals)
- Authoritative lifecycle: predict → assess → decide → log
- Data products per stage (Prediction, Signal(s), Assessment, Decision, FailureRecord)
- Async semantics (what must be async, what can be off-thread)
- Schema stability rules (“locked” public surface; additive-only changes)
- Policy semantics (aleatoric vs epistemic behaviors)
- Latency/tiering guarantees
- Drift stance for Phase 0 (non-blocking + shadow mode)

C) “Hello World” Implementation Checklist (step-by-step)
A numbered checklist that a developer can follow to get a running demo:
- FastAPI endpoint that wraps a sklearn model
- MAPIE adapter producing UncertaintyScore(aleatoric, epistemic)
- Threshold policy (configurable; treat thresholds as governance)
- Logging of decisions/failures with trace_id
- Basic tests

D) Output Format & Constraints
- Do NOT ask clarifying questions unless a missing detail blocks delivery.
- If you must assume something, list assumptions explicitly.
- Provide rationale, but do NOT reveal private chain-of-thought; use concise bullet justifications.
- Keep everything production-oriented (names, file paths, concrete steps).

# Success criteria (you must meet these)
- A developer can start implementing immediately without additional architecture meetings.
- The delegation map clearly separates “judgment work” vs “mechanical work.”
- The contract is stable enough that adapters/policies can change behind it without breaking clients.
- Drift is explicitly non-blocking and initially shadow-mode.
- The UncertaintyAdapter interface is TorchCP-ready without breaking changes later.
