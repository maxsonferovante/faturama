"""Monthly spend query."""

from __future__ import annotations

from pathlib import Path

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.summary_repository import SummaryRepository


def execute(database_path: str, user_id: str, month: str, card: str | None = None) -> list[dict]:
    year_str, month_str = month.split("-", 1)
    rows = SummaryRepository(connect(Path(database_path))).list_summaries(user_id, int(year_str), int(month_str))
    if card:
        rows = [row for row in rows if row["card_fingerprint"] == card]
    return rows
