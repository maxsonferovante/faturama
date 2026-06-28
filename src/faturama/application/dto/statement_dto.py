"""Statement DTOs."""

from __future__ import annotations

from faturama.shared.pydantic_compat import BaseModel


class StatementDTO(BaseModel):
    statement_id: str
    document_id: str
    user_id: str
    issuer_name: str | None = None
    card_fingerprint: str
    billing_year: int
    billing_month: int
    statement_status: str
    parse_confidence: float
