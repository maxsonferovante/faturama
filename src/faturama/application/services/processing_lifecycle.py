"""Helpers for lifecycle transitions and status projections."""

from __future__ import annotations

from datetime import UTC, datetime
import uuid

from faturama.domain.value_objects.processing_status import ProcessingStatus


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def lifecycle_event_payload(
    *,
    processing_id: str,
    status: ProcessingStatus,
    status_detail: str | None = None,
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "event_id": str(uuid.uuid4()),
        "processing_id": processing_id,
        "event_name": status.value.lower(),
        "status": status.value,
        "status_detail": status_detail,
        "payload_json": payload or {},
        "created_at": utc_now(),
    }


def status_projection_payload(
    *,
    processing_id: str,
    status: ProcessingStatus,
    document_id: str | None = None,
    file_hash: str | None = None,
    status_detail: str | None = None,
    result_reference: str | None = None,
    artifact_manifest_id: str | None = None,
    transitioned_at: str | None = None,
) -> dict[str, object]:
    timestamp = transitioned_at or utc_now()
    return {
        "processing_id": processing_id,
        "document_id": document_id,
        "file_hash": file_hash,
        "current_status": status.value,
        "is_terminal": 1 if status.is_terminal else 0,
        "status_detail": status_detail,
        "result_reference": result_reference,
        "artifact_manifest_id": artifact_manifest_id,
        "review_required": 1 if status.review_required else 0,
        "last_transition_at": timestamp,
        "updated_at": timestamp,
    }
