"""Use case for syncing lifecycle events and read-model status."""

from __future__ import annotations

from faturama.application.services.processing_lifecycle import lifecycle_event_payload, status_projection_payload
from faturama.domain.value_objects.processing_status import ProcessingStatus


def update_processing_status(
    *,
    processing_id: str,
    status: ProcessingStatus,
    job_repository: object,
    status_repository: object,
    status_detail: str | None = None,
    document_id: str | None = None,
    file_hash: str | None = None,
    result_reference: str | None = None,
    artifact_manifest_id: str | None = None,
) -> None:
    event_payload = lifecycle_event_payload(
        processing_id=processing_id,
        status=status,
        status_detail=status_detail,
    )
    projection_payload = status_projection_payload(
        processing_id=processing_id,
        status=status,
        document_id=document_id,
        file_hash=file_hash,
        status_detail=status_detail,
        result_reference=result_reference,
        artifact_manifest_id=artifact_manifest_id,
        transitioned_at=event_payload["created_at"],
    )
    job_repository.record_lifecycle_event(event_payload)
    status_repository.upsert_status(projection_payload)
