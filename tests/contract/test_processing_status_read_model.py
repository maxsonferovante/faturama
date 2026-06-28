from __future__ import annotations

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.processing_status_repository import ProcessingStatusRepository


def test_processing_status_read_model_contract(temp_db):
    repository = ProcessingStatusRepository(connect(temp_db))
    repository.upsert_status(
        {
            "processing_id": "evt-1",
            "document_id": "doc-1",
            "file_hash": "sha256",
            "current_status": "RUNNING",
            "is_terminal": 0,
            "status_detail": "extraindo documento",
            "result_reference": None,
            "artifact_manifest_id": None,
            "review_required": 0,
            "last_transition_at": "2026-06-28T12:01:12Z",
            "updated_at": "2026-06-28T12:01:12Z",
        }
    )
    row = repository.get_status("evt-1")
    assert row is not None
    assert row["current_status"] == "RUNNING"
    assert row["is_terminal"] == 0
