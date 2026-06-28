"""Transaction DTOs."""

from __future__ import annotations

from faturama.shared.pydantic_compat import BaseModel


class TransactionDTO(BaseModel):
    transaction_id: str
    statement_id: str
    description_raw: str
    amount: str
    transaction_kind: str
    parse_confidence: float
    review_status: str
