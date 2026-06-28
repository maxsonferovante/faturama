"""Transaction line entity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransactionLine:
    transaction_id: str
    statement_id: str
    document_id: str
    card_fingerprint: str
    description_raw: str
    amount: str
    transaction_kind: str
    line_hash: str
    parse_confidence: float
    review_status: str
    decision_state: str
    source_evidence_id: str | None = None
    source_strategy: str = "rule"
    currency: str = "BRL"
    posted_date: str | None = None
    purchase_date: str | None = None
    description_normalized: str | None = None
    merchant_normalized: str | None = None
    raw_text: str | None = None
    page_number: int | None = None
    is_installment: bool = False
    installment_current: int | None = None
    installment_total: int | None = None
