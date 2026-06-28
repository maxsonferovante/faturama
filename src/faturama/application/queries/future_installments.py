"""Future installments query."""

from __future__ import annotations

from pathlib import Path

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.installment_repository import InstallmentRepository


def execute(database_path: str, user_id: str, month: str, card: str | None = None) -> list[dict]:
    year_str, month_str = month.split("-", 1)
    rows = InstallmentRepository(connect(Path(database_path))).list_projections(int(year_str), int(month_str), user_id)
    if card:
        rows = [row for row in rows if row["card_fingerprint"] == card]
    return rows
