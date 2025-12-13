from __future__ import annotations

import pytest

from model_guardian.schemas.config import GuardianConfig, GuardianSettings


def test_guardian_config_defaults():
    cfg = GuardianConfig()
    assert cfg.nonblocking_timeout_ms == 10
    assert cfg.drift_mode == "shadow"
    assert cfg.freeze_raw_artifacts is True


def test_guardian_config_validation():
    with pytest.raises(ValueError):
        GuardianConfig(nonblocking_timeout_ms=-1)

    with pytest.raises(ValueError):
        GuardianConfig(drift_mode="nope")  # type: ignore[arg-type]


def test_guardian_settings_to_config(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MODEL_GUARDIAN_NONBLOCKING_TIMEOUT_MS", "25")
    monkeypatch.setenv("MODEL_GUARDIAN_DRIFT_MODE", "enforce")
    monkeypatch.setenv("MODEL_GUARDIAN_FREEZE_RAW_ARTIFACTS", "false")

    s = GuardianSettings()
    cfg = s.to_config()

    assert cfg.nonblocking_timeout_ms == 25
    assert cfg.drift_mode == "enforce"
    assert cfg.freeze_raw_artifacts is False
