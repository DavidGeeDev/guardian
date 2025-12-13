from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


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
    # source of the signal (adapter/provider name)
    provider: str = "unknown"
    type: SignalType
    severity: SignalSeverity = SignalSeverity.INFO

    # optional human-readable message (kept separate from `value` for ergonomics)
    message: Optional[str] = None

    # value is intentionally flexible; we still keep the schema strict around the envelope
    value: Any
    details: Optional[dict[str, Any]] = None

    # hint to downstream systems about whether it was computed in the critical path
    blocking: bool = True

    @classmethod
    def info(
        cls,
        *,
        name: str,
        provider: str = "unknown",
        type: SignalType = SignalType.CUSTOM,
        value: Any = None,
        message: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        blocking: bool = True,
    ) -> "Signal":
        if value is None:
            value = {}
        if details is None and message is not None:
            details = {"message": message}
        return cls(
            name=name,
            provider=provider,
            type=type,
            severity=SignalSeverity.INFO,
            value=value,
            message=message,
            details=details,
            blocking=blocking,
        )

    @classmethod
    def warning(
        cls,
        *,
        name: str,
        provider: str = "unknown",
        type: SignalType = SignalType.CUSTOM,
        value: Any = None,
        message: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        blocking: bool = True,
    ) -> "Signal":
        if value is None:
            value = {}
        if details is None and message is not None:
            details = {"message": message}
        return cls(
            name=name,
            provider=provider,
            type=type,
            severity=SignalSeverity.WARNING,
            value=value,
            message=message,
            details=details,
            blocking=blocking,
        )

    @classmethod
    def critical(
        cls,
        *,
        name: str,
        provider: str = "unknown",
        type: SignalType = SignalType.CUSTOM,
        value: Any = None,
        message: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        blocking: bool = True,
    ) -> "Signal":
        if value is None:
            value = {}
        if details is None and message is not None:
            details = {"message": message}
        return cls(
            name=name,
            provider=provider,
            type=type,
            severity=SignalSeverity.CRITICAL,
            value=value,
            message=message,
            details=details,
            blocking=blocking,
        )
