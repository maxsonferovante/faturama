from __future__ import annotations

from datetime import datetime

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.processing_status_repository import ProcessingStatusRepository
from faturama.interface.worker.runner import run_processing_message
from tests.async_helpers import write_async_source


def test_status_propagation_latency_is_under_30_seconds(async_settings):
    write_async_source(
        async_settings.artifact_cache_dir.parent / "object-store",
        "pre-processamento-faturama",
        "incoming/invoice-latency.pdf",
    )
    started = datetime.now()
    run_processing_message(
        {
            "processing_id": "evt-latency",
            "bucket": "pre-processamento-faturama",
            "object_key": "incoming/invoice-latency.pdf",
            "event_time": "2026-06-28T12:00:00Z",
            "source": "aws.s3.eventbridge",
            "metadata": {},
        },
        settings=async_settings,
    )
    status = ProcessingStatusRepository(connect(async_settings.database_path)).get_status("evt-latency")
    assert status is not None
    assert (datetime.now() - started).total_seconds() < 30
