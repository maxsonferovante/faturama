"""Installment plan DTOs."""

from __future__ import annotations

from faturama.shared.pydantic_compat import BaseModel


class InstallmentPlanDTO(BaseModel):
    installment_plan_id: str
    card_fingerprint: str
    description_normalized: str
    installment_amount: str
    installment_total: int
    canonical_key: str
