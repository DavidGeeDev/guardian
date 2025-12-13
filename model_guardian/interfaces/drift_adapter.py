from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar

from .signal_provider import SignalProvider

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class DriftAdapter(SignalProvider[InputT, OutputT], ABC, Generic[InputT, OutputT]):
    """A drift detector adapter.

    Drift checks should be *non-blocking* by default; use background execution and emit signals
    opportunistically (or as last-known-state). This follows the design goal of keeping inference
    latency low while still collecting safety signals.
    """

    name: str = "drift"
    blocking: bool = False
