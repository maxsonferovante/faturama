from __future__ import annotations

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.processing_status_repository import ProcessingStatusRepository
from faturama.interface.worker.runner import run_processing_message
from tests.async_helpers import write_async_source


def test_event_driven_dispatch_e2e(async_settings):
    write_async_source(
        async_settings.artifact_cache_dir.parent / "object-store",
        "pre-processamento-faturama",
        "incoming/invoice-2026-04.pdf",
    )
    result = run_processing_message(
        {
            "processing_id": "evt-1",
            "bucket": "pre-processamento-faturama",
            "object_key": "incoming/invoice-2026-04.pdf",
            "event_time": "2026-06-28T12:00:00Z",
            "source": "s3",
            "metadata": {},
        },
        settings=async_settings,
    )
    repository = ProcessingStatusRepository(connect(async_settings.database_path))
    status = repository.get_status("evt-1")
    assert result["status"] in {"SUCCESS", "REVIEW_REQUIRED", "PARTIAL"}
    assert status is not None
    assert status["current_status"] == result["status"]
