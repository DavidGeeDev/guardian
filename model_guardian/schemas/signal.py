from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class SignalType(str, Enum):
    UNCERTAINTY = "uncertainty"
    DRIFT = "drift"
    OOD = "ood"
    QUALITY = "quality"
    CUSTOM = "custom"


class SignalSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Signal(BaseModel):
    """Atomic measurement emitted by a provider (UQ, drift, etc.)."""

    model_config = ConfigDict(extra="forbid")

    name: str
    type: SignalType
    severity: SignalSeverity = SignalSeverity.INFO

    # value is intentionally flexible; we still keep the schema strict around the envelope
    value: Any
    details: Optional[dict[str, Any]] = None

    # hint to downstream systems about whether it was computed in the critical path
    blocking: bool = True
