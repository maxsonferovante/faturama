"""Installment plan entity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InstallmentPlan:
    installment_plan_id: str
    user_id: str
    card_fingerprint: str
    installment_type: str
    description_anchor: str
    description_normalized: str
    installment_amount: str
    installment_total: int
    canonical_key: str
    plan_status: str = "active"
    plan_confidence: float = 1.0
    merchant_normalized: str | None = None
    origin_purchase_date: str | None = None
    first_seen_statement_id: str | None = None
    last_seen_statement_id: str | None = None
    matching_strategy: str = "canonical-key"
    runtime_source: str = "official"
    legacy_status: str = "active"
