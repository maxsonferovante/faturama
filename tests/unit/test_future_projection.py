from __future__ import annotations

from faturama.domain.services.future_projection import project_future_installments


def test_project_future_installments_rolls_months_forward():
    projections = project_future_installments(
        {
            "installment_plan_id": "plan-1",
            "card_fingerprint": "inter:1234",
            "installment_total": 4,
            "installment_amount": "R$ 100,00",
            "plan_confidence": 0.95,
        },
        current_installment=2,
        billing_year=2026,
        billing_month=12,
    )
    assert [(item["projected_billing_year"], item["projected_billing_month"]) for item in projections] == [(2027, 1), (2027, 2)]
