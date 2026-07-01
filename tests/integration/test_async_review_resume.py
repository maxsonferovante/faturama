from __future__ import annotations

from faturama.infrastructure.database.postgres import connect
from faturama.infrastructure.checkpoint.postgres_checkpoint_store import PostgresCheckpointStore


def test_checkpoint_store_can_save_and_restore(async_settings):
    connection = connect(async_settings.database_dsn)
    try:
        store = PostgresCheckpointStore(connection)
        checkpoint_id = store.save(
            "job-1",
            "thread-1",
            "resolve_ambiguities",
            {"status": "REVIEW_REQUIRED"},
            review_required=True,
        )
        latest = store.latest("job-1")
        assert latest is not None
        assert latest["checkpoint_id"] == checkpoint_id
        store.mark_restored(checkpoint_id)
        restored = store.latest("job-1")
        assert restored["checkpoint_status"] == "restored"
    finally:
        connection.close()

