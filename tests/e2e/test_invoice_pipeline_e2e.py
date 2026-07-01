from __future__ import annotations

from faturama.application.queries.future_installments import execute as future_installments
from faturama.application.queries.monthly_spend import execute as monthly_spend
from faturama.application.queries.remaining_balance import execute as remaining_balance
from faturama.application.use_cases.process_invoice import process_invoice
from faturama.application.use_cases.review_queue import list_pending, resolve_item
from faturama.infrastructure.config.settings import load_settings
from faturama.interface.cli.composition import read_model_query_service
from tests.integration.test_monthly_queries import require_postgres_dsn, reset_database


def test_invoice_pipeline_e2e(invoice_dir, temp_db, monkeypatch):
    dsn = require_postgres_dsn(monkeypatch)
    reset_database(dsn)
    settings = load_settings()
    first = process_invoice(str(invoice_dir / "invoice-2026-04.pdf"), "demo-user", settings)
    assert first["review_items_opened"] == 1

    with read_model_query_service(settings) as query_service:
        review_id = list_pending(query_service, "demo-user")[0]["review_item_id"]
        resolve_item(query_service, review_id, "accepted", "Confirmado")

    second = process_invoice(str(invoice_dir / "invoice-2026-05.pdf"), "demo-user", settings)
    assert second["transactions_persisted"] == 2

    with read_model_query_service(settings) as query_service:
        spend = monthly_spend(query_service, "demo-user", "2026-05")
        future = future_installments(query_service, "demo-user", "2026-06")
        balance = remaining_balance(query_service, "demo-user")
    assert spend[0]["new_purchase_total"] == "300.00"
    assert future[0]["projected_installment_number"] == 4
    assert balance[0]["remaining_balance"] == "2960.23"
