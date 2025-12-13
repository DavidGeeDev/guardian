from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from model_guardian.schemas import (
    GuardianDecision,
    Prediction,
    RequestContext,
    Signal,
    UncertaintyScore,
)

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class AbstentionPolicy(ABC, Generic[InputT, OutputT]):
    """Policy engine: converts signals into a decision."""

    @abstractmethod
    async def decide(
        self,
        *,
        x: InputT,
        prediction: Prediction[OutputT],
        uncertainty: UncertaintyScore,
        signals: Sequence[Signal],
        context: RequestContext,
    ) -> GuardianDecision:
        raise NotImplementedError
