from __future__ import annotations

from faturama.domain.services.monthly_summary import build_summary


def test_build_summary_splits_new_purchase_and_installments():
    summary = build_summary(
        user_id="demo",
        statement={"card_fingerprint": "inter:1234", "billing_year": 2026, "billing_month": 4},
        transactions=[
            {"transaction_kind": "new_purchase", "amount": "R$ 200,00"},
            {"transaction_kind": "installment_charge", "amount": "R$ 422,89"},
        ],
        future_balance="3383.12",
    )
    assert summary["new_purchase_total"] == "200.00"
    assert summary["installment_charge_total"] == "422.89"
