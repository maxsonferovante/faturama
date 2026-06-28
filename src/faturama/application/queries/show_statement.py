"""Show statement query."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.statement_repository import StatementRepository


def execute(database_path: str, statement_id: str) -> dict | None:
    repo = StatementRepository(connect(Path(database_path)))
    statement = repo.get_statement(statement_id)
    return asdict(statement) if statement else None
