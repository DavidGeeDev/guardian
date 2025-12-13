from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from model_guardian.schemas import Prediction, RequestContext, Signal

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class SignalProvider(ABC, Generic[InputT, OutputT]):
    """A pluggable signal generator (uncertainty, drift, OOD, etc.)."""

    name: str = "provider"

    # Whether this provider should be awaited in the request critical path.
    # Drift providers default to False (non-blocking).
    blocking: bool = True

    @abstractmethod
    async def compute(
        self,
        *,
        x: InputT,
        prediction: Prediction[OutputT],
        context: RequestContext,
    ) -> Sequence[Signal]:
        raise NotImplementedError
