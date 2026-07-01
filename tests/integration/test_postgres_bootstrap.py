from __future__ import annotations

from faturama.infrastructure.checkpoint.postgres_checkpoint_store import PostgresCheckpointStore
from faturama.infrastructure.database.postgres import connect


def test_postgres_bootstrap_creates_core_tables(postgres_dsn):
    connection = connect(postgres_dsn)
    try:
        names = {
            row["tablename"]
            for row in connection.execute(
                """
                SELECT tablename
                FROM pg_catalog.pg_tables
                WHERE schemaname = current_schema()
                """
            ).fetchall()
        }
    finally:
        connection.close()

    assert {
        "documents",
        "statements",
        "transactions",
        "installment_plans",
        "projections",
        "summaries",
        "review_items",
        "decision_records",
        "workflow_checkpoints",
    } <= names


def test_postgres_checkpoint_store_round_trip(postgres_dsn):
    connection = connect(postgres_dsn)
    try:
        store = PostgresCheckpointStore(connection)
        checkpoint_id = store.save(
            job_id="job-postgres-bootstrap",
            thread_id="thread-postgres-bootstrap",
            node_name="extract_document",
            state={"step": "extract_document"},
            review_required=True,
        )

        checkpoint = store.latest("job-postgres-bootstrap")
        assert checkpoint is not None
        assert checkpoint["checkpoint_id"] == checkpoint_id
        assert checkpoint["state"] == {"step": "extract_document"}
        assert checkpoint["review_required"] is True

        store.mark_restored(checkpoint_id)
        restored = store.latest("job-postgres-bootstrap")
        assert restored is not None
        assert restored["checkpoint_status"] == "restored"
        assert restored["restored_at"] is not None
    finally:
        connection.close()
