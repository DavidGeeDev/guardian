from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any

from model_guardian.schemas import Prediction, RequestContext

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class ModelAdapter(ABC, Generic[InputT, OutputT]):
    """Abstracts model inference behind an awaitable API."""

    @abstractmethod
    async def predict(self, x: InputT, *, context: RequestContext) -> Prediction[OutputT]:
        raise NotImplementedError

    @property
    def model_id(self) -> str | None:
        return None

    @property
    def model_version(self) -> str | None:
        return None
