from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UncertaintyScore(BaseModel):
    """Uncertainty with explicit Aleatoric vs Epistemic components.

    Scores are normalized to [0, 1] where:
    - higher aleatoric => more inherent ambiguity / noise
    - higher epistemic => more model ignorance / out-of-depth risk
    """

    model_config = ConfigDict(extra="forbid")

    aleatoric: float = Field(ge=0.0, le=1.0)
    epistemic: float = Field(ge=0.0, le=1.0)

    # Optional interpretable artifacts
    prediction_set_size: int | None = Field(default=None, ge=0)
    coverage: float | None = Field(default=None, ge=0.0, le=1.0)
    method: str = "unknown"
