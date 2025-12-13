from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from model_guardian.core.utils import run_sync
from model_guardian.interfaces import TelemetrySink
from model_guardian.schemas import FailureRecord, GuardianDecision, Prediction, RequestContext, Signal, UncertaintyScore


class JsonlFileSink(TelemetrySink):
    """Append-only JSONL telemetry sink (Phase 0 friendly).

    Writes are done in a threadpool to avoid blocking the event loop.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def _append(self, payload: dict[str, Any]) -> None:
        line = json.dumps(payload, default=str) + "\n"

        def _write():
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line)

        await run_sync(_write)

    async def emit_event(
        self,
        *,
        context: RequestContext,
        prediction: Prediction,
        uncertainty: UncertaintyScore,
        decision: GuardianDecision,
        signals: list[Signal],
    ) -> None:
        await self._append(
            {
                "type": "event",
                "context": context.model_dump(),
                "prediction": prediction.model_dump(),
                "uncertainty": uncertainty.model_dump(),
                "decision": decision.model_dump(),
                "signals": [s.model_dump() for s in signals],
            }
        )

    async def emit_failure(
        self,
        *,
        context: RequestContext,
        failure: FailureRecord,
        decision: GuardianDecision,
        signals: list[Signal],
    ) -> None:
        await self._append(
            {
                "type": "failure",
                "context": context.model_dump(),
                "failure": failure.model_dump(),
                "decision": decision.model_dump(),
                "signals": [s.model_dump() for s in signals],
            }
        )
