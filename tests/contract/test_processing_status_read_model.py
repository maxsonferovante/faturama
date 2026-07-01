from __future__ import annotations

from faturama.infrastructure.database.postgres import connect
from faturama.infrastructure.repositories.processing_status_repository import ProcessingStatusRepository


def test_processing_status_read_model_contract(temp_db):
    connection = connect(temp_db)
    try:
        repository = ProcessingStatusRepository(connection)
        repository.upsert_status(
            {
                "processing_id": "evt-1",
                "document_id": "doc-1",
                "file_hash": "sha256",
                "current_status": "RUNNING",
                "is_terminal": False,
                "status_detail": "extraindo documento",
                "result_reference": None,
                "artifact_manifest_id": None,
                "review_required": False,
                "last_transition_at": "2026-06-28T12:01:12Z",
                "updated_at": "2026-06-28T12:01:12Z",
            }
        )
        row = repository.get_status("evt-1")
        assert row is not None
        assert row["current_status"] == "RUNNING"
        assert row["is_terminal"] is False
    finally:
        connection.close()

