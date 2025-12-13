from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings


class GuardianConfig(BaseModel):
    """Runtime tuning knobs for the guardian.

    These are kept as a lightweight schema so callers can pass config objects
    without env wiring. If you want env-based config, use :class:`GuardianSettings`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    # Non-blocking safety checks should not inflate request p99.
    nonblocking_timeout_ms: int = Field(default=10, ge=0)

    # Drift behavior:
    # - off: do not run drift at all
    # - shadow: run drift asynchronously and log it, but do not let it affect policy
    # - enforce: include drift signals in the policy inputs
    drift_mode: Literal["off", "shadow", "enforce"] = "shadow"

    # If True, deep-freeze Prediction.raw artifacts to prevent accidental mutation.
    freeze_raw_artifacts: bool = True


class GuardianSettings(BaseSettings):
    """Env-backed settings for deploying Model Guardian.

    Environment variables:
      - MODEL_GUARDIAN_NONBLOCKING_TIMEOUT_MS
      - MODEL_GUARDIAN_DRIFT_MODE
      - MODEL_GUARDIAN_FREEZE_RAW_ARTIFACTS
    """

    nonblocking_timeout_ms: int = 10
    drift_mode: Literal["off", "shadow", "enforce"] = "shadow"
    freeze_raw_artifacts: bool = True

    model_config = ConfigDict(env_prefix="MODEL_GUARDIAN_", extra="ignore")

    def to_config(self) -> GuardianConfig:
        return GuardianConfig(
            nonblocking_timeout_ms=self.nonblocking_timeout_ms,
            drift_mode=self.drift_mode,
            freeze_raw_artifacts=self.freeze_raw_artifacts,
        )
