from __future__ import annotations

import json
from pathlib import Path

from faturama.application.use_cases.build_processing_command import build_processing_command
from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.upload_grant_repository import UploadGrantRepository


def test_s3_event_is_normalized_and_saved(temp_db):
    payload = json.loads(Path("tests/integration/fixtures/s3_event.json").read_text(encoding="utf-8"))
    normalized, command = build_processing_command(payload, artifact_prefix="processed")
    repository = UploadGrantRepository(connect(temp_db))
    repository.save_source_event(normalized)
    saved = repository.get_source_event_by_dedupe_key(normalized["dedupe_key"])
    assert saved is not None
    assert command.object_key == "incoming/invoice-2026-04.pdf"
    assert saved["bucket_name"] == "pre-processamento-faturama"
