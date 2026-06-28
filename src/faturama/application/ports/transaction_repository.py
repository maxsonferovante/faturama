"""Transaction repository port."""

from __future__ import annotations

from typing import Protocol

from faturama.domain.entities.transaction_line import TransactionLine


class TransactionRepository(Protocol):
    def save_transactions(self, transactions: list[TransactionLine]) -> None: ...
    def list_transactions(self, statement_id: str) -> list[TransactionLine]: ...
