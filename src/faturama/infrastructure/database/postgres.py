"""Generic SQL connection helpers for async runtime."""

from __future__ import annotations

from pathlib import Path
import re
import sqlite3
from typing import Any
from urllib.parse import urlparse

from faturama.infrastructure.database.schema import initialize_schema


_NAMED_PARAM_PATTERN = re.compile(r":([A-Za-z_][A-Za-z0-9_]*)")
_INSERT_OR_REPLACE_PATTERN = re.compile(
    r"""
    INSERT\s+OR\s+REPLACE\s+INTO\s+
    (?P<table>[A-Za-z_][A-Za-z0-9_]*)\s*
    \((?P<columns>[^)]+)\)\s*
    VALUES\s*\((?P<values>[^)]+)\)
    """,
    re.IGNORECASE | re.VERBOSE | re.DOTALL,
)


class PostgresCompatConnection:
    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def execute(self, query: str, params: Any = None) -> Any:
        adapted_query, adapted_params = _adapt_sql(query, params)
        if adapted_params is None:
            return self._connection.execute(adapted_query)
        return self._connection.execute(adapted_query, adapted_params)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._connection, name)


def _adapt_sql(query: str, params: Any) -> tuple[str, Any]:
    adapted_query = _adapt_insert_or_replace(query)
    if isinstance(params, dict):
        adapted_query = _NAMED_PARAM_PATTERN.sub(r"%(\1)s", adapted_query)
        return adapted_query, _normalize_params(params)
    if params is not None:
        adapted_query = adapted_query.replace("?", "%s")
    return adapted_query, _normalize_params(params)


def _adapt_insert_or_replace(query: str) -> str:
    match = _INSERT_OR_REPLACE_PATTERN.search(query)
    if not match:
        return query

    table_name = match.group("table")
    columns = [column.strip() for column in match.group("columns").split(",")]
    values = match.group("values").strip()
    conflict_column = columns[0]
    update_columns = [column for column in columns if column != conflict_column]
    update_assignments = ", ".join(f"{column} = EXCLUDED.{column}" for column in update_columns)
    replacement = (
        f"INSERT INTO {table_name} ({', '.join(columns)}) "
        f"VALUES ({values}) "
        f"ON CONFLICT ({conflict_column}) DO UPDATE SET {update_assignments}"
    )
    return _INSERT_OR_REPLACE_PATTERN.sub(replacement, query, count=1)


def _normalize_params(params: Any) -> Any:
    if isinstance(params, bool):
        return int(params)
    if isinstance(params, dict):
        return {key: _normalize_params(value) for key, value in params.items()}
    if isinstance(params, tuple):
        return tuple(_normalize_params(value) for value in params)
    if isinstance(params, list):
        return [_normalize_params(value) for value in params]
    return params


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
        from psycopg.rows import dict_row
    except Exception as exc:  # pragma: no cover - exercised only without psycopg installed
        raise RuntimeError("psycopg is required for PostgreSQL DSNs") from exc

    connection = PostgresCompatConnection(psycopg.connect(dsn, row_factory=dict_row))
    initialize_schema(connection)
    return connection
