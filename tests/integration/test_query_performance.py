from __future__ import annotations

import time

from faturama.application.queries.monthly_spend import execute as monthly_spend
from faturama.application.use_cases.process_invoice import process_invoice
from faturama.infrastructure.config.settings import load_settings
from faturama.application.services.query_service import read_model_query_service
from tests.integration.test_monthly_queries import require_postgres_dsn, reset_database


def test_monthly_query_finishes_within_goal(invoice_dir, temp_db, monkeypatch):
    dsn = require_postgres_dsn(monkeypatch)
    reset_database(dsn)
    settings = load_settings()
    process_invoice(str(invoice_dir / "invoice-2026-04.pdf"), "demo-user", settings)
    started = time.perf_counter()
    with read_model_query_service(settings) as query_service:
        monthly_spend(query_service, "demo-user", "2026-04")
    elapsed = time.perf_counter() - started
    assert elapsed < 5
