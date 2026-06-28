"""Invoice statement entity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InvoiceStatement:
    statement_id: str
    document_id: str
    user_id: str
    issuer_name: str | None
    card_fingerprint: str
    billing_year: int
    billing_month: int
    statement_status: str
    parse_confidence: float
    card_label: str | None = None
    card_last4: str | None = None
    card_holder_name: str | None = None
    statement_due_date: str | None = None
    statement_close_date: str | None = None
    statement_issue_date: str | None = None
    statement_total_amount: str | None = None
    minimum_payment_amount: str | None = None
    credit_limit_amount: str | None = None
    currency: str = "BRL"
    runtime_source: str = "official"
    legacy_status: str = "active"
    partial_status: str = "complete"
