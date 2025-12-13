from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from model_guardian.schemas import GuardianResponse, RequestContext

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class GuardianMiddleware(ABC, Generic[InputT, OutputT]):
    """Main wrapper contract."""

    @abstractmethod
    async def __call__(self, x: InputT, *, context: RequestContext | None = None) -> GuardianResponse[OutputT]:
        raise NotImplementedError
