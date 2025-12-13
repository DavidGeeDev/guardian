from __future__ import annotations

import asyncio
from typing import Iterable, List, Optional

from model_guardian.interfaces import TelemetrySink
from model_guardian.schemas import (
    FailureRecord,
    GuardianDecision,
    Prediction,
    RequestContext,
    Signal,
    UncertaintyScore,
)


class TelemetryFanout(TelemetrySink):
    """Fan-out telemetry to multiple sinks."""

    def __init__(self, sinks: Optional[Iterable[TelemetrySink]] = None):
        self._sinks: List[TelemetrySink] = list(sinks or [])

    def add(self, sink: TelemetrySink) -> None:
        self._sinks.append(sink)

    async def emit_event(
        self,
        *,
        context: RequestContext,
        prediction: Prediction,
        uncertainty: UncertaintyScore,
        decision: GuardianDecision,
        signals: list[Signal],
    ) -> None:
        if not self._sinks:
            return
        await asyncio.gather(
            *[
                s.emit_event(
                    context=context, prediction=prediction, uncertainty=uncertainty, decision=decision, signals=signals
                )
                for s in self._sinks
            ],
            return_exceptions=True,
        )

    async def emit_failure(
        self,
        *,
        context: RequestContext,
        failure: FailureRecord,
        decision: GuardianDecision,
        signals: list[Signal],
    ) -> None:
        if not self._sinks:
            return
        await asyncio.gather(
            *[s.emit_failure(context=context, failure=failure, decision=decision, signals=signals) for s in self._sinks],
            return_exceptions=True,
        )
