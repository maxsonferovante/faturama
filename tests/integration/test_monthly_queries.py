from __future__ import annotations

from faturama.application.queries.current_installments import execute as current_installments
from faturama.application.queries.future_installments import execute as future_installments
from faturama.application.queries.monthly_spend import execute as monthly_spend
from faturama.application.queries.remaining_balance import execute as remaining_balance
from faturama.application.use_cases.process_invoice import process_invoice
from faturama.infrastructure.config.settings import load_settings


def test_monthly_queries_return_expected_read_models(invoice_dir, temp_db):
    settings = load_settings()
    process_invoice(str(invoice_dir / "invoice-2026-04.pdf"), "demo-user", settings)
    process_invoice(str(invoice_dir / "invoice-2026-05.pdf"), "demo-user", settings)

    spend = monthly_spend(str(temp_db), "demo-user", "2026-04")
    observed = current_installments(str(temp_db), "demo-user", "2026-05")
    projected = future_installments(str(temp_db), "demo-user", "2026-06")
    balance = remaining_balance(str(temp_db), "demo-user")

    assert spend[0]["installment_charge_total"] == "422.89"
    assert any(item["installment_current"] == 3 for item in observed)
    assert any(item["projected_installment_number"] == 4 for item in projected)
    assert balance[0]["remaining_balance"] == "2960.23"
