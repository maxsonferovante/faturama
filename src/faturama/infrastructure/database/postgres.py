"""Generic SQL connection helpers for async runtime."""

from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Any
from urllib.parse import urlparse

from faturama.infrastructure.database.schema import initialize_schema


def _as_db_path(dsn: str) -> Path:
    if dsn.startswith("sqlite:///"):
        return Path(dsn.removeprefix("sqlite:///"))
    return Path(dsn)


def connect_from_dsn(dsn: str) -> Any:
    if dsn.startswith("sqlite:///") or dsn.endswith(".sqlite3") or dsn.endswith(".db"):
        database_path = _as_db_path(dsn)
        database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        initialize_schema(connection)
        return connection

    parsed = urlparse(dsn)
    if parsed.scheme not in {"postgresql", "postgres"}:
        raise ValueError(f"Unsupported DSN scheme: {parsed.scheme}")

    try:
        import psycopg
    except Exception as exc:  # pragma: no cover - exercised only without psycopg installed
        raise RuntimeError("psycopg is required for PostgreSQL DSNs") from exc

    connection = psycopg.connect(dsn)
    initialize_schema(connection)
    return connection
