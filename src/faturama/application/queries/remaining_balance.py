"""Remaining balance query."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.installment_repository import InstallmentRepository


def execute(database_path: str, user_id: str, card: str | None = None, plan_id: str | None = None) -> list[dict]:
    repo = InstallmentRepository(connect(Path(database_path)))
    plans = repo.list_plans(user_id)
    results: list[dict] = []
    for plan in plans:
        if card and plan.card_fingerprint != card:
            continue
        if plan_id and plan.installment_plan_id != plan_id:
            continue
        projections = [
            row
            for row in repo.list_projections(9999, 12, None)  # no-op default, replaced below
        ]
        del projections
        rows = repo.connection.execute(
            "SELECT * FROM projections WHERE installment_plan_id = ? ORDER BY projected_billing_year, projected_billing_month",
            (plan.installment_plan_id,),
        ).fetchall()
        amount = Decimal("0")
        for row in rows:
            value = row["projected_amount"].replace("R$", "").replace(".", "").replace(",", ".").strip()
            amount += Decimal(value)
        results.append(
            {
                "installment_plan_id": plan.installment_plan_id,
                "card_fingerprint": plan.card_fingerprint,
                "description_anchor": plan.description_anchor,
                "installment_total": plan.installment_total,
                "plan_status": plan.plan_status,
                "remaining_balance": f"{amount:.2f}",
            }
        )
    return results
