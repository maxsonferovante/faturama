"""Normalize incoming source events into the canonical processing contract."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
from typing import Any
import uuid

from faturama.application.dto.processing_command_dto import ProcessingCommandDTO


def _now() -> str:
    return datetime.now(UTC).isoformat()


def build_dedupe_key(bucket: str, object_key: str, event_time: str, etag: str | None, object_version: str | None) -> str:
    raw = "|".join([bucket, object_key, event_time, etag or "", object_version or ""])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize_source_event(payload: dict[str, Any], *, artifact_prefix: str, source: str = "s3") -> dict[str, Any]:
    records = payload.get("Records")
    if isinstance(records, list) and records:
        record = records[0]
        bucket = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]
        object_version = record["s3"]["object"].get("versionId")
        etag = record["s3"]["object"].get("eTag")
        event_time = record.get("eventTime") or _now()
        metadata = {"object_version": object_version, "etag": etag}
        upload_grant_id = record.get("messageAttributes", {}).get("upload_grant_id")
        processing_id = str(uuid.uuid4())
    else:
        bucket = payload["bucket"]
        object_key = payload["object_key"]
        object_version = payload.get("object_version")
        etag = payload.get("etag")
        event_time = payload.get("event_time") or _now()
        metadata = dict(payload.get("metadata", {}))
        upload_grant_id = payload.get("upload_grant_id")
        processing_id = payload.get("processing_id", str(uuid.uuid4()))
    dedupe_key = build_dedupe_key(bucket, object_key, event_time, etag, object_version)
    return {
        "source_event_id": payload.get("source_event_id", str(uuid.uuid4())),
        "bucket_name": bucket,
        "object_key": object_key,
        "object_version": object_version,
        "event_time": event_time,
        "event_name": payload.get("event_name", "ObjectCreated"),
        "object_etag": etag,
        "upload_grant_id": upload_grant_id,
        "source_system": source,
        "received_at": _now(),
        "dedupe_key": dedupe_key,
        "processing_command": ProcessingCommandDTO(
            processing_id=processing_id,
            bucket=bucket,
            object_key=object_key,
            event_time=event_time,
            source=source,
            upload_grant_id=upload_grant_id,
            metadata=metadata,
            artifact_prefix=artifact_prefix,
        ).model_dump(),
    }
