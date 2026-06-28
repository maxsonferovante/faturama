from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from faturama.interface.worker.runner import run_processing_message
from tests.async_helpers import write_async_source


def test_async_runtime_handles_burst_of_20_uploads(async_settings):
    root = async_settings.artifact_cache_dir.parent / "object-store"
    for index in range(20):
        write_async_source(root, "pre-processamento-faturama", f"incoming/invoice-{index}.pdf")

    def _run(index: int) -> str:
        result = run_processing_message(
            {
                "processing_id": f"evt-{index}",
                "bucket": "pre-processamento-faturama",
                "object_key": f"incoming/invoice-{index}.pdf",
                "event_time": "2026-06-28T12:00:00Z",
                "source": "s3",
                "metadata": {},
            },
            settings=async_settings,
        )
        return result["status"]

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(_run, range(20)))

    assert len(results) == 20
    assert sum(status in {"SUCCESS", "PARTIAL", "REVIEW_REQUIRED"} for status in results) >= 18
