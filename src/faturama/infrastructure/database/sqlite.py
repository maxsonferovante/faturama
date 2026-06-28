"""SQLite connection helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from faturama.infrastructure.database.schema import initialize_schema


def connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    initialize_schema(connection)
    return connection
