from __future__ import annotations

import json
from pathlib import Path

from faturama.application.use_cases.build_processing_command import build_processing_command
from faturama.infrastructure.database.postgres import connect
from faturama.infrastructure.repositories.processing_status_repository import ProcessingStatusRepository
from faturama.interface.worker.runner import run_processing_message
from tests.async_helpers import write_async_source


def test_event_driven_dispatch_e2e(async_settings):
    payload = json.loads(Path("tests/integration/fixtures/s3_event.json").read_text(encoding="utf-8"))
    normalized, command = build_processing_command(payload, artifact_prefix="processed")
    write_async_source(
        async_settings.artifact_cache_dir.parent / "object-store",
        "pre-processamento-faturama",
        "incoming/invoice-2026-04.pdf",
    )
    result = run_processing_message(command.model_dump(), settings=async_settings)
    connection = connect(async_settings.database_dsn)
    try:
        repository = ProcessingStatusRepository(connection)
        status = repository.get_status(command.processing_id)
        assert result["status"] in {"SUCCESS", "REVIEW_REQUIRED", "PARTIAL"}
        assert status is not None
        assert normalized["source_event_id"] == payload["id"]
        assert status["current_status"] == result["status"]
    finally:
        connection.close()

