"""List statement query."""

from __future__ import annotations

from pathlib import Path

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.statement_repository import StatementRepository


def parse_period(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    year_str, month_str = value.split("-", 1)
    return int(year_str), int(month_str)


def execute(database_path: str, user_id: str, card: str | None = None, from_: str | None = None, to: str | None = None) -> list[dict]:
    repo = StatementRepository(connect(Path(database_path)))
    return repo.list_statements_filtered(user_id, card, parse_period(from_), parse_period(to))
