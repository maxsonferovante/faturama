from __future__ import annotations

from faturama.application.use_cases.process_invoice import process_invoice
from faturama.application.use_cases.review_queue import list_pending, resolve_item
from faturama.infrastructure.config.settings import load_settings
from faturama.infrastructure.database.postgres import connect
from faturama.application.services.query_service import read_model_query_service


def test_review_workflow_lists_and_resolves_low_confidence_items(invoice_dir, temp_db):
    settings = load_settings()
    result = process_invoice(str(invoice_dir / "invoice-2026-04.pdf"), "demo-user", settings)
    assert result["review_items_opened"] == 1

    with read_model_query_service(settings) as query_service:
        queue = list_pending(query_service, "demo-user")
        assert len(queue) == 1

        resolved = resolve_item(query_service, queue[0]["review_item_id"], "accepted", "Confirmado")
        assert resolved["status"] == "resolved"

    resumed = process_invoice(str(invoice_dir / "invoice-2026-04.pdf"), "demo-user", settings)
    assert resumed["review_items_opened"] == 0

    connection = connect(temp_db)
    try:
        row = connection.execute(
            "SELECT partial_status, statement_status FROM statements WHERE statement_id = %s",
            (resumed["statement_ids"][0],),
        ).fetchone()
        assert row["partial_status"] == "complete"
        assert row["statement_status"] == "parsed"
    finally:
        connection.close()

