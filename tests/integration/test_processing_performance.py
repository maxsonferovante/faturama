from __future__ import annotations

import time

from faturama.application.use_cases.process_invoice import process_invoice
from faturama.infrastructure.config.settings import load_settings


def test_processing_finishes_within_goal(invoice_dir, temp_db):
    settings = load_settings()
    started = time.perf_counter()
    process_invoice(str(invoice_dir / "invoice-2026-04.pdf"), "demo-user", settings)
    elapsed = time.perf_counter() - started
    assert elapsed < 60
