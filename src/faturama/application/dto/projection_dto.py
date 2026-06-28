"""Projection DTOs."""

from __future__ import annotations

from faturama.shared.pydantic_compat import BaseModel


class ProjectionDTO(BaseModel):
    projection_id: str
    installment_plan_id: str
    projected_billing_year: int
    projected_billing_month: int
    projected_installment_number: int
    projected_amount: str
