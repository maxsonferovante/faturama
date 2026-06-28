"""Installment repository port."""

from __future__ import annotations

from typing import Protocol

from faturama.domain.entities.future_installment_projection import FutureInstallmentProjection
from faturama.domain.entities.installment_plan import InstallmentPlan


class InstallmentRepository(Protocol):
    def save_plan(self, plan: InstallmentPlan) -> None: ...
    def list_plans(self, user_id: str) -> list[InstallmentPlan]: ...
    def save_projections(self, projections: list[FutureInstallmentProjection]) -> None: ...
