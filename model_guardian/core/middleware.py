from __future__ import annotations

import asyncio
import time
import logging
from typing import Generic, Optional, Sequence, TypeVar

from model_guardian.interfaces import DriftAdapter, ModelAdapter, TelemetrySink, UncertaintyAdapter
from model_guardian.schemas import (
    GuardianConfig,
    FailureRecord,
    FailureType,
    GuardianAction,
    GuardianDecision,
    GuardianResponse,
    Prediction,
    RequestContext,
    Signal,
    SignalSeverity,
    SignalType,
    UncertaintyScore,
)
from .policies import ThresholdAbstentionPolicy
from .telemetry import TelemetryFanout
from .utils import deep_freeze

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")

logger = logging.getLogger(__name__)


class DefaultGuardian(Generic[InputT, OutputT]):
    """Default Phase 0 Guardian.

    Execution model:
    - model inference: awaited
    - uncertainty: awaited in critical path (blocking)
    - drift: scheduled non-blocking by default; included if it completes quickly
    - policy: awaited
    - telemetry: emitted in background
    """

    def __init__(
        self,
        *,
        model: ModelAdapter[InputT, OutputT],
        uncertainty: UncertaintyAdapter[InputT, OutputT],
        drift: DriftAdapter[InputT, OutputT] | None = None,
        policy: ThresholdAbstentionPolicy[InputT, OutputT] | None = None,
        telemetry: TelemetrySink | None = None,
        config: GuardianConfig | None = None,
    ):
        self._model = model
        self._uncertainty = uncertainty
        self._drift = drift
        self._policy = policy or ThresholdAbstentionPolicy()
        self._telemetry = telemetry or TelemetryFanout()
        self._config = config or GuardianConfig()
        self._nb_timeout = self._config.nonblocking_timeout_ms / 1000.0

    async def __call__(self, x: InputT, *, context: RequestContext | None = None) -> GuardianResponse[OutputT]:
        ctx = context or RequestContext()

        # 1) model inference (awaitable)
        t0 = time.perf_counter()
        pred: Prediction[OutputT] = await self._model.predict(x, context=ctx)
        pred = pred.model_copy(
            update={
                "model_id": pred.model_id or getattr(self._model, "model_id", None),
                "model_version": pred.model_version or getattr(self._model, "model_version", None),
                "latency_ms": (time.perf_counter() - t0) * 1000.0,
            }
        )

        # Optional strictness: deep-freeze raw artifacts to prevent accidental mutation.
        # (Phase 0 defaults to True; callers can disable for debugging/perf.)
        if self._config.freeze_raw_artifacts and pred.raw is not None:
            # Convert to a concrete dict first so MappingProxyType etc. behave predictably.
            pred = pred.model_copy(update={"raw": deep_freeze(dict(pred.raw))})

        # 2) signal computation (uncertainty + drift)
        # We keep two lists:
        # - policy_signals: what the policy is allowed to consider (shadow drift excludes drift signals)
        # - all_signals: what we return and emit to telemetry (includes drift results / timeout markers)
        policy_signals: list[Signal] = []

        # drift is non-blocking; schedule it early
        drift_task: asyncio.Task[Sequence[Signal]] | None = None
        if self._drift is not None and self._config.drift_mode != "off":
            drift_task = asyncio.create_task(self._drift.compute(x=x, prediction=pred, context=ctx))

        uncertainty_score: UncertaintyScore = await self._uncertainty.quantify(x=x, prediction=pred, context=ctx)
        uq_signals = list(await self._uncertainty.compute(x=x, prediction=pred, context=ctx))
        policy_signals.extend(uq_signals)

        drift_signals: list[Signal] = []
        if drift_task is not None:
            try:
                drift_signals = list(await asyncio.wait_for(drift_task, timeout=self._nb_timeout))
            except TimeoutError:
                # allow it to continue in background; do not cancel
                drift_signals = [
                    Signal.warning(
                        name="drift.timeout",
                        provider=getattr(self._drift, "name", type(self._drift).__name__),
                        type=SignalType.DRIFT,
                        value={"timeout_ms": self._config.nonblocking_timeout_ms},
                        message="Drift check exceeded non-blocking timeout; continuing in background.",
                        blocking=False,
                    )
                ]
            except asyncio.CancelledError:
                raise
            except Exception as e:
                # Do not silently swallow drift adapter failures.
                # We keep the request path safe by degrading to an error signal,
                # while still surfacing the exception for debugging.
                logger.exception("Drift adapter compute failed", exc_info=e)
                drift_signals = [
                    Signal(
                        name="drift.error",
                        provider=getattr(self._drift, "name", type(self._drift).__name__),
                        type=SignalType.DRIFT,
                        severity=SignalSeverity.CRITICAL,
                        value={"error": type(e).__name__},
                        message=str(e),
                        details={"error_type": type(e).__name__},
                        blocking=False,
                    )
                ]

        # Drift handling modes:
        # - shadow: record drift signals but do not let them influence policy
        # - enforce: include drift signals in the policy inputs
        if self._config.drift_mode == "enforce":
            policy_signals.extend(drift_signals)

        # all_signals are what we emit/return (includes drift results regardless of mode)
        all_signals: list[Signal] = list(policy_signals)
        if self._config.drift_mode != "enforce":
            all_signals.extend(drift_signals)

        if self._config.drift_mode == "shadow" and drift_task is not None:
            all_signals.append(
                Signal.info(
                    name="drift.shadow",
                    provider="guardian",
                    type=SignalType.DRIFT,
                    value={"mode": "shadow"},
                    message="Drift check ran in shadow mode (not policy-enforcing).",
                    blocking=False,
                )
            )

        # 3) policy decision
        decision: GuardianDecision = await self._policy.decide(
            x=x,
            prediction=pred,
            uncertainty=uncertainty_score,
            signals=policy_signals,
            context=ctx,
        )

        # 4) shape final response
        if decision.action in (GuardianAction.ABSTAIN, GuardianAction.BLOCK):
            failure_type = FailureType.EPISTEMIC_OOD if uncertainty_score.epistemic >= 0.5 else FailureType.POLICY_BLOCK
            failure = FailureRecord(
                failure_type=failure_type,
                message=decision.reason,
                details={
                    "uncertainty": uncertainty_score.model_dump(),
                    "decision": decision.model_dump(),
                },
            )
            # telemetry async
            asyncio.create_task(
                self._telemetry.emit_failure(
                    context=ctx,
                    failure=failure,
                    decision=decision,
                    signals=all_signals,
                )
            )
            return GuardianResponse(
                prediction=None,
                failure=failure,
                uncertainty=uncertainty_score,
                decision=decision,
                signals=all_signals,
            )

        asyncio.create_task(
            self._telemetry.emit_event(
                context=ctx,
                prediction=pred,
                uncertainty=uncertainty_score,
                decision=decision,
                signals=all_signals,
            )
        )

        return GuardianResponse(
            prediction=pred,
            failure=None,
            uncertainty=uncertainty_score,
            decision=decision,
            signals=all_signals,
        )
