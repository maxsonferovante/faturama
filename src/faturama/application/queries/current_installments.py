"""Current installments query."""

from __future__ import annotations

from pathlib import Path

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.transaction_repository import TransactionRepository


def execute(database_path: str, user_id: str, month: str, card: str | None = None) -> list[dict]:
    year_str, month_str = month.split("-", 1)
    return TransactionRepository(connect(Path(database_path))).list_by_month(
        user_id=user_id,
        year=int(year_str),
        month=int(month_str),
        kind="installment_charge",
        card_fingerprint=card,
    )
