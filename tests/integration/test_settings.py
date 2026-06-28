from __future__ import annotations

from faturama.infrastructure.config.settings import load_settings


def test_load_settings_uses_environment(temp_db, monkeypatch):
    monkeypatch.setenv("FATURAMA_CONFIDENCE_THRESHOLD", "0.91")
    settings = load_settings()
    assert settings.database_path == temp_db
    assert settings.confidence_threshold == 0.91
