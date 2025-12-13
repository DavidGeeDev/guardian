from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar, Any

from model_guardian.schemas import Prediction, RequestContext, Signal, SignalSeverity, SignalType, UncertaintyScore
from .signal_provider import SignalProvider

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class UncertaintyAdapter(SignalProvider[InputT, OutputT], ABC, Generic[InputT, OutputT]):
    """Specialized provider that produces an UncertaintyScore.

    Design constraints:
    - Phase 0: MAPIE (NumPy/scikit-learn)
    - Future: TorchCP (PyTorch tensors / GPU)
    To avoid breaking changes, `x` and `prediction.raw` are treated as *transport envelopes*:
    implementations should accept ndarray-like OR tensor-like objects without changing signatures.
    """

    name: str = "uncertainty"
    blocking: bool = True

    @abstractmethod
    async def quantify(
        self,
        *,
        x: InputT,
        prediction: Prediction[OutputT],
        context: RequestContext,
    ) -> UncertaintyScore:
        raise NotImplementedError

    async def compute(
        self,
        *,
        x: InputT,
        prediction: Prediction[OutputT],
        context: RequestContext,
    ) -> Sequence[Signal]:
        u = await self.quantify(x=x, prediction=prediction, context=context)
        # Provide a minimal standard signal envelope.
        sev = SignalSeverity.INFO
        if u.epistemic >= 0.8:
            sev = SignalSeverity.CRITICAL
        elif u.aleatoric >= 0.8:
            sev = SignalSeverity.WARNING
        return [
            Signal(
                name="uncertainty.score",
                type=SignalType.UNCERTAINTY,
                severity=sev,
                value={"aleatoric": u.aleatoric, "epistemic": u.epistemic},
                details=u.model_dump(),
                blocking=True,
            )
        ]
