"""Checkpoint store compatible with PostgreSQL DSNs and sqlite fallback."""

from __future__ import annotations

from pathlib import Path

from faturama.infrastructure.database.langgraph_checkpoint import SQLiteCheckpointStore


class PostgresCheckpointStore(SQLiteCheckpointStore):
    def __init__(self, dsn: str | Path) -> None:
        path = (
            Path(str(dsn).removeprefix("sqlite:///"))
            if str(dsn).startswith("sqlite:///")
            else Path("data/faturama-async-checkpoints.sqlite3")
        )
        super().__init__(path)
