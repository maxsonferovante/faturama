from __future__ import annotations

import os

import pytest

from faturama.application.queries.current_installments import execute as current_installments
from faturama.application.queries.future_installments import execute as future_installments
from faturama.application.queries.monthly_spend import execute as monthly_spend
from faturama.application.queries.remaining_balance import execute as remaining_balance
from faturama.application.use_cases.process_invoice import process_invoice
from faturama.infrastructure.config.settings import load_settings
from faturama.infrastructure.database.postgres import connect_from_dsn
from faturama.application.services.query_service import read_model_query_service


TABLES = (
    "processing_status_read_model",
    "artifact_manifests",
    "processing_lifecycle_events",
    "processing_jobs",
    "source_object_events",
    "upload_authorization_grants",
    "workflow_checkpoints",
    "decision_records",
    "review_items",
    "summaries",
    "projections",
    "installment_plans",
    "transactions",
    "evidences",
    "statements",
    "documents",
)


def require_postgres_dsn(monkeypatch: pytest.MonkeyPatch) -> str:
    dsn = os.getenv("FATURAMA_TEST_DB_DSN") or os.getenv("FATURAMA_DB_DSN")
    if not dsn or not dsn.startswith(("postgresql://", "postgres://")):
        pytest.skip("PostgreSQL DSN required in FATURAMA_TEST_DB_DSN or FATURAMA_DB_DSN")
    monkeypatch.setenv("FATURAMA_DB_DSN", dsn)
    return dsn


def reset_database(dsn: str) -> None:
    connection = connect_from_dsn(dsn)
    try:
        for table in TABLES:
            connection.execute(f"DELETE FROM {table}")
        connection.commit()
    finally:
        connection.close()


def test_monthly_queries_return_expected_read_models(invoice_dir, temp_db, monkeypatch):
    dsn = require_postgres_dsn(monkeypatch)
    reset_database(dsn)
    settings = load_settings()
    process_invoice(str(invoice_dir / "invoice-2026-04.pdf"), "demo-user", settings)
    process_invoice(str(invoice_dir / "invoice-2026-05.pdf"), "demo-user", settings)

    with read_model_query_service(settings) as query_service:
        spend = monthly_spend(query_service, "demo-user", "2026-04")
        observed = current_installments(query_service, "demo-user", "2026-05")
        projected = future_installments(query_service, "demo-user", "2026-06")
        balance = remaining_balance(query_service, "demo-user")

    assert spend[0]["installment_charge_total"] == "422.89"
    assert any(item["installment_current"] == 3 for item in observed)
    assert any(item["projected_installment_number"] == 4 for item in projected)
    assert balance[0]["remaining_balance"] == "2960.23"
