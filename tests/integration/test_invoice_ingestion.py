from __future__ import annotations

from faturama.application.use_cases.process_invoice import process_invoice
from faturama.infrastructure.config.settings import load_settings
from faturama.infrastructure.database.postgres import connect


def test_first_time_ingestion_is_idempotent(invoice_dir, temp_db):
    settings = load_settings()
    pdf = str(invoice_dir / "invoice-2026-04.pdf")
    first = process_invoice(pdf, "demo-user", settings)
    second = process_invoice(pdf, "demo-user", settings)

    assert first["document_id"] == second["document_id"]
    assert first["statement_ids"] == second["statement_ids"]

    connection = connect(temp_db)
    try:
        tx_count = connection.execute("SELECT COUNT(*) AS count FROM transactions").fetchone()["count"]
        doc_count = connection.execute("SELECT COUNT(*) AS count FROM documents").fetchone()["count"]
        assert doc_count == 1
        assert tx_count == 3
    finally:
        connection.close()

