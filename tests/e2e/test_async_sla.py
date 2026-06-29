from __future__ import annotations

from datetime import datetime

from faturama.interface.worker.runner import run_processing_message
from tests.async_helpers import write_async_source


def test_async_pipeline_completes_within_5_minutes(async_settings):
    write_async_source(
        async_settings.artifact_cache_dir.parent / "object-store",
        "pre-processamento-faturama",
        "incoming/invoice-sla.pdf",
    )
    started = datetime.now()
    result = run_processing_message(
        {
            "processing_id": "evt-sla",
            "bucket": "pre-processamento-faturama",
            "object_key": "incoming/invoice-sla.pdf",
            "event_time": "2026-06-28T12:00:00Z",
            "source": "aws.s3.eventbridge",
            "metadata": {},
        },
        settings=async_settings,
    )
    assert result["status"] in {"SUCCESS", "REVIEW_REQUIRED", "PARTIAL"}
    assert (datetime.now() - started).total_seconds() < 300
