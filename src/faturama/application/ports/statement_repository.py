"""Statement repository port."""

from __future__ import annotations

from typing import Protocol

from faturama.domain.entities.invoice_statement import InvoiceStatement


class StatementRepository(Protocol):
    def save_statement(self, statement: InvoiceStatement) -> None: ...
    def list_statements(self, user_id: str) -> list[InvoiceStatement]: ...
