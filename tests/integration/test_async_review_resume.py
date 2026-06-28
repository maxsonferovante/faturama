from __future__ import annotations

from faturama.infrastructure.database.postgres_checkpoint import PostgresCheckpointStore


def test_checkpoint_store_can_save_and_restore(async_settings):
    store = PostgresCheckpointStore(async_settings.checkpoint_database_path)
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
