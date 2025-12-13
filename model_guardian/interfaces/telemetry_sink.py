from __future__ import annotations

from abc import ABC, abstractmethod

from model_guardian.schemas import FailureRecord, GuardianDecision, Prediction, RequestContext, Signal, UncertaintyScore


class TelemetrySink(ABC):
    """Receives telemetry asynchronously (events, failures, decisions)."""

    @abstractmethod
    async def emit_event(
        self,
        *,
        context: RequestContext,
        prediction: Prediction,
        uncertainty: UncertaintyScore,
        decision: GuardianDecision,
        signals: list[Signal],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def emit_failure(
        self,
        *,
        context: RequestContext,
        failure: FailureRecord,
        decision: GuardianDecision,
        signals: list[Signal],
    ) -> None:
        raise NotImplementedError
