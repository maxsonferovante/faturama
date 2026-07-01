from __future__ import annotations

import pytest

from faturama.infrastructure.config.settings import load_settings
from faturama.infrastructure.database.postgres import DatabaseConfigurationError


def test_load_settings_uses_environment(monkeypatch):
    monkeypatch.setenv("FATURAMA_CONFIDENCE_THRESHOLD", "0.91")
    monkeypatch.setenv("FATURAMA_DB_DSN", "postgresql://faturama:faturama@localhost:5432/faturama")
    settings = load_settings()
    assert settings.database_dsn == "postgresql://faturama:faturama@localhost:5432/faturama"
    assert settings.confidence_threshold == 0.91


def test_load_settings_requires_database_dsn(monkeypatch):
    monkeypatch.delenv("FATURAMA_DB_DSN", raising=False)

    with pytest.raises(DatabaseConfigurationError, match="FATURAMA_DB_DSN is required"):
        load_settings()


@pytest.mark.parametrize(
    "dsn",
    [
        "sqlite:///tmp/faturama.sqlite3",
        "data/faturama.sqlite3",
        "mysql://faturama:faturama@localhost/faturama",
    ],
)
def test_load_settings_rejects_non_postgres_dsn(monkeypatch, dsn):
    monkeypatch.setenv("FATURAMA_DB_DSN", dsn)

    with pytest.raises(DatabaseConfigurationError, match="postgresql:// or postgres://"):
        load_settings()
