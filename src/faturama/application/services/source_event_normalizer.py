"""Normalize incoming source events into the canonical processing contract."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
from typing import Any
import uuid
from urllib.parse import unquote_plus

from faturama.application.dto.processing_command_dto import ProcessingCommandDTO


def _now() -> str:
    return datetime.now(UTC).isoformat()


def build_dedupe_key(bucket: str, object_key: str, event_time: str, etag: str | None, object_version: str | None) -> str:
    raw = "|".join([bucket, object_key, event_time, etag or "", object_version or ""])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _eventbridge_processing_id(event_id: str | None) -> str:
    if event_id:
        return f"evtbridge-{event_id}"
    return str(uuid.uuid4())


def normalize_source_event(
    payload: dict[str, Any],
    *,
    artifact_prefix: str,
    source: str = "aws.s3.eventbridge",
) -> dict[str, Any]:
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
        source_event_id = payload.get("source_event_id", str(uuid.uuid4()))
        event_name = payload.get("event_name", "ObjectCreated")
    elif payload.get("source") == "aws.s3" and isinstance(payload.get("detail"), dict):
        detail = payload["detail"]
        bucket = detail["bucket"]["name"]
        object_key = unquote_plus(detail["object"]["key"])
        object_version = detail["object"].get("version-id")
        etag = detail["object"].get("etag")
        event_time = payload.get("time") or _now()
        source_event_id = payload.get("id", str(uuid.uuid4()))
        upload_grant_id = payload.get("upload_grant_id")
        processing_id = payload.get("processing_id", _eventbridge_processing_id(source_event_id))
        event_name = payload.get("detail-type", "Object Created")
        metadata = {
            "source_event_id": source_event_id,
            "eventbridge_id": source_event_id,
            "etag": etag,
            "version_id": object_version,
            "sequencer": detail["object"].get("sequencer"),
            "request_id": detail.get("request-id"),
            "requester": detail.get("requester"),
            "reason": detail.get("reason"),
        }
    else:
        bucket = payload["bucket"]
        object_key = payload["object_key"]
        object_version = payload.get("object_version")
        etag = payload.get("etag")
        event_time = payload.get("event_time") or _now()
        metadata = dict(payload.get("metadata", {}))
        upload_grant_id = payload.get("upload_grant_id")
        source_event_id = payload.get(
            "source_event_id",
            metadata.get("source_event_id") or metadata.get("eventbridge_id") or str(uuid.uuid4()),
        )
        processing_id = payload.get("processing_id", _eventbridge_processing_id(str(source_event_id)))
        event_name = payload.get("event_name", "Object Created")
    dedupe_key = build_dedupe_key(bucket, object_key, event_time, etag, object_version)
    metadata.setdefault("source_event_id", source_event_id)
    metadata.setdefault("etag", etag)
    metadata.setdefault("version_id", object_version)
    return {
        "source_event_id": source_event_id,
        "bucket_name": bucket,
        "object_key": object_key,
        "object_version": object_version,
        "event_time": event_time,
        "event_name": event_name,
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
