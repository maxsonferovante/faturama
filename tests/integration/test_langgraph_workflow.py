from __future__ import annotations

from faturama.application.use_cases.process_invoice import process_invoice
from faturama.infrastructure.config.settings import load_settings
from faturama.infrastructure.database.postgres import connect


def test_langgraph_workflow_persists_checkpoint_history(invoice_dir, temp_db):
    settings = load_settings()
    result = process_invoice(str(invoice_dir / "invoice-2026-04.pdf"), "demo-user", settings)

    checkpoint_db = connect(temp_db)
    try:
        rows = checkpoint_db.execute(
            """
            SELECT node_name, checkpoint_status, review_required
            FROM workflow_checkpoints
            WHERE job_id = %s
            ORDER BY created_at
            """,
            (result["job_id"],),
        ).fetchall()

        node_names = [row["node_name"] for row in rows]
        assert node_names == [
            "extract_document",
            "parse_statement",
            "classify_transactions",
            "resolve_ambiguities",
            "persist_canonical_data",
            "finalize_job",
        ]
        assert rows[3]["checkpoint_status"] == "active"
        assert rows[3]["review_required"] is True
    finally:
        checkpoint_db.close()

