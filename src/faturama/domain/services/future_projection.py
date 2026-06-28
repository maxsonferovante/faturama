"""Future installment projections."""

from __future__ import annotations

import uuid


def project_future_installments(plan: dict, current_installment: int | None, billing_year: int, billing_month: int) -> list[dict]:
    if current_installment is None:
        return []
    projections: list[dict] = []
    total = int(plan["installment_total"])
    year = billing_year
    month = billing_month
    for number in range(current_installment + 1, total + 1):
        month += 1
        if month > 12:
            month = 1
            year += 1
        projections.append(
            {
                "projection_id": str(
                    uuid.uuid5(
                        uuid.NAMESPACE_URL,
                        f"{plan['installment_plan_id']}:{year}-{month:02d}:{number}",
                    )
                ),
                "installment_plan_id": plan["installment_plan_id"],
                "card_fingerprint": plan["card_fingerprint"],
                "projected_billing_year": year,
                "projected_billing_month": month,
                "projected_installment_number": number,
                "projected_amount": plan["installment_amount"],
                "projection_status": "projected",
                "projection_confidence": plan["plan_confidence"],
            }
        )
    return projections
