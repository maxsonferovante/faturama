from __future__ import annotations

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.upload_grant_repository import UploadGrantRepository


def test_signed_upload_grant_can_be_persisted_and_marked_used(temp_db):
    repository = UploadGrantRepository(connect(temp_db))
    repository.upsert_grant(
        {
            "upload_grant_id": "grant-1",
            "authorized_bucket": "pre-processamento-faturama",
            "authorized_object_key": "incoming/invoice.pdf",
            "granted_to": "partner-a",
            "granted_by": "issuer-api",
            "granted_at": "2026-06-28T12:00:00Z",
            "expires_at": "2026-06-28T12:05:00Z",
            "upload_completed_at": None,
            "grant_status": "issued",
            "trace_context": {"trace_id": "abc"},
        }
    )
    repository.mark_used("grant-1", "2026-06-28T12:01:00Z")
    saved = repository.get_grant("grant-1")
    assert saved is not None
    assert saved["grant_status"] == "used"
    assert saved["authorized_bucket"] == "pre-processamento-faturama"
