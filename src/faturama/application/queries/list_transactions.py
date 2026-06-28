"""List statement transactions query."""

from __future__ import annotations

from pathlib import Path

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.transaction_repository import TransactionRepository


def execute(
    database_path: str,
    statement_id: str,
    kind: str | None = None,
    installments_only: bool = False,
    review_status: str | None = None,
) -> list[dict]:
    repo = TransactionRepository(connect(Path(database_path)))
    return repo.list_by_statement(statement_id, kind=kind, installments_only=installments_only, review_status=review_status)
