from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class FailureType(str, Enum):
    """Failure taxonomy for Model Guardian.

    Phase 0 distinguishes:
    - Aleatoric uncertainty: irreducible data noise / ambiguity
    - Epistemic uncertainty: model ignorance / out-of-depth
    - Distribution shift categories
    """

    ALEATORIC_AMBIGUITY = "aleatoric_ambiguity"
    EPISTEMIC_OOD = "epistemic_out_of_depth"

    COVARIATE_SHIFT = "covariate_shift"
    LABEL_SHIFT = "label_shift"
    CONCEPT_DRIFT = "concept_drift"

    RELIABILITY_FAILURE = "reliability_failure"
    ROBUSTNESS_FAILURE = "robustness_failure"

    POLICY_BLOCK = "policy_block"
    SYSTEM_ERROR = "system_error"
    TIMEOUT = "timeout"


class FailureRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    failure_type: FailureType
    message: str = Field(min_length=1)
    details: Optional[dict[str, Any]] = None
