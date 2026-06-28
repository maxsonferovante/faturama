"""Future installment projection entity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FutureInstallmentProjection:
    projection_id: str
    installment_plan_id: str
    card_fingerprint: str
    projected_billing_year: int
    projected_billing_month: int
    projected_installment_number: int
    projected_amount: str
    projection_status: str = "projected"
    projection_confidence: float = 1.0
