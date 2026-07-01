from __future__ import annotations

from faturama.infrastructure.database.postgres import connect
from faturama.infrastructure.repositories.processing_status_repository import ProcessingStatusRepository
from faturama.interface.worker.runner import run_processing_message
from tests.async_helpers import write_async_source


def test_async_pipeline_reprocessing_is_idempotent(async_settings):
    root = async_settings.artifact_cache_dir.parent / "object-store"
    write_async_source(root, "pre-processamento-faturama", "incoming/invoice-2026-04.pdf")
    for processing_id in ("evt-1", "evt-2"):
        run_processing_message(
            {
                "processing_id": processing_id,
                "bucket": "pre-processamento-faturama",
                "object_key": "incoming/invoice-2026-04.pdf",
                "event_time": "2026-06-28T12:00:00Z",
                "source": "aws.s3.eventbridge",
                "metadata": {},
            },
            settings=async_settings,
        )
    connection = connect(async_settings.database_dsn)
    try:
        repository = ProcessingStatusRepository(connection)
        first = repository.get_status("evt-1")
        second = repository.get_status("evt-2")
        assert first is not None and second is not None
        assert first["file_hash"] == second["file_hash"]
    finally:
        connection.close()

