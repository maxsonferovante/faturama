"""LangGraph runtime wrappers backed by PostgreSQL settings."""

from __future__ import annotations

from typing import Any

from langgraph.checkpoint.memory import MemorySaver

from faturama.infrastructure.checkpoint.postgres_checkpoint_store import PostgresCheckpointStore
from faturama.infrastructure.database.postgres import connect


class LangGraphPostgresRuntime:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.connection = None
        self.checkpoint_store = None
        self.checkpointer = None

    def open(self) -> PostgresCheckpointStore:
        self.connection = connect(self.dsn)
        self.checkpoint_store = PostgresCheckpointStore(self.connection)
        self.checkpointer = MemorySaver()
        return self.checkpoint_store

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            self.checkpoint_store = None
            self.checkpointer = None

