from __future__ import annotations

import time

from faturama.application.queries.monthly_spend import execute as monthly_spend
from faturama.application.use_cases.process_invoice import process_invoice
from faturama.infrastructure.config.settings import load_settings


def test_monthly_query_finishes_within_goal(invoice_dir, temp_db):
    settings = load_settings()
    process_invoice(str(invoice_dir / "invoice-2026-04.pdf"), "demo-user", settings)
    started = time.perf_counter()
    monthly_spend(str(temp_db), "demo-user", "2026-04")
    elapsed = time.perf_counter() - started
    assert elapsed < 5
