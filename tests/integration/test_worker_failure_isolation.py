from __future__ import annotations

import pytest

from faturama.interface.worker.runner import run_processing_message
from tests.async_helpers import write_async_source


def test_worker_failure_does_not_prevent_next_processing(async_settings):
    with pytest.raises(FileNotFoundError):
        run_processing_message(
            {
                "processing_id": "evt-missing",
                "bucket": "pre-processamento-faturama",
                "object_key": "incoming/missing.pdf",
                "event_time": "2026-06-28T12:00:00Z",
                "source": "s3",
                "metadata": {},
            },
            settings=async_settings,
        )

    write_async_source(
        async_settings.artifact_cache_dir.parent / "object-store",
        "pre-processamento-faturama",
        "incoming/invoice-valid.pdf",
    )
    result = run_processing_message(
        {
            "processing_id": "evt-valid",
            "bucket": "pre-processamento-faturama",
            "object_key": "incoming/invoice-valid.pdf",
            "event_time": "2026-06-28T12:00:00Z",
            "source": "s3",
            "metadata": {},
        },
        settings=async_settings,
    )
    assert result["status"] in {"SUCCESS", "PARTIAL", "REVIEW_REQUIRED"}
