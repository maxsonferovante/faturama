from __future__ import annotations

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.processing_job_repository import ProcessingJobRepository
from faturama.interface.worker.runner import run_processing_message
from tests.async_helpers import write_async_source


def test_operational_diagnostics_capture_lifecycle_events(async_settings):
    write_async_source(
        async_settings.artifact_cache_dir.parent / "object-store",
        "pre-processamento-faturama",
        "incoming/invoice-diagnostics.pdf",
    )
    run_processing_message(
        {
            "processing_id": "evt-diagnostics",
            "bucket": "pre-processamento-faturama",
            "object_key": "incoming/invoice-diagnostics.pdf",
            "event_time": "2026-06-28T12:00:00Z",
            "source": "aws.s3.eventbridge",
            "metadata": {},
        },
        settings=async_settings,
    )
    repository = ProcessingJobRepository(connect(async_settings.database_path))
    job = repository.get_job("evt-diagnostics")
    assert job is not None
    assert job["current_status"] in {"SUCCESS", "PARTIAL", "REVIEW_REQUIRED"}
