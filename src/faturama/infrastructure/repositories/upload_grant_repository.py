from __future__ import annotations

import json
from typing import Any


class UploadGrantRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def upsert_grant(self, payload: dict[str, Any]) -> None:
        row = dict(payload)
        row.setdefault("trace_context", "{}")
        if isinstance(row["trace_context"], dict):
            row["trace_context"] = json.dumps(row["trace_context"], ensure_ascii=False)
        self.connection.execute(
            """
            INSERT INTO upload_authorization_grants (
                upload_grant_id, authorized_bucket, authorized_object_key, granted_to, granted_by, granted_at,
                expires_at, upload_completed_at, grant_status, trace_context
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (upload_grant_id) DO UPDATE SET
                authorized_bucket = EXCLUDED.authorized_bucket,
                authorized_object_key = EXCLUDED.authorized_object_key,
                granted_to = EXCLUDED.granted_to,
                granted_by = EXCLUDED.granted_by,
                granted_at = EXCLUDED.granted_at,
                expires_at = EXCLUDED.expires_at,
                upload_completed_at = EXCLUDED.upload_completed_at,
                grant_status = EXCLUDED.grant_status,
                trace_context = EXCLUDED.trace_context
            """,
            (
                row.get("upload_grant_id"),
                row.get("authorized_bucket"),
                row.get("authorized_object_key"),
                row.get("granted_to"),
                row.get("granted_by"),
                row.get("granted_at"),
                row.get("expires_at"),
                row.get("upload_completed_at"),
                row.get("grant_status"),
                row.get("trace_context"),
            ),
        )

    def mark_used(self, upload_grant_id: str, uploaded_at: str) -> None:
        self.connection.execute(
            """
            UPDATE upload_authorization_grants
            SET upload_completed_at = %s, grant_status = 'used'
            WHERE upload_grant_id = %s
            """,
            (uploaded_at, upload_grant_id),
        )

    def get_grant(self, upload_grant_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM upload_authorization_grants WHERE upload_grant_id = %s",
            (upload_grant_id,),
        ).fetchone()
        return dict(row) if row else None

    def save_source_event(self, payload: dict[str, Any]) -> None:
        row = dict(payload)
        self.connection.execute(
            """
            INSERT INTO source_object_events (
                source_event_id, bucket_name, object_key, object_version, event_time, event_name, object_etag,
                upload_grant_id, source_system, received_at, dedupe_key
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (dedupe_key) DO UPDATE SET
                source_event_id = EXCLUDED.source_event_id,
                bucket_name = EXCLUDED.bucket_name,
                object_key = EXCLUDED.object_key,
                object_version = EXCLUDED.object_version,
                event_time = EXCLUDED.event_time,
                event_name = EXCLUDED.event_name,
                object_etag = EXCLUDED.object_etag,
                upload_grant_id = EXCLUDED.upload_grant_id,
                source_system = EXCLUDED.source_system,
                received_at = EXCLUDED.received_at
            """,
            (
                row.get("source_event_id"),
                row.get("bucket_name"),
                row.get("object_key"),
                row.get("object_version"),
                row.get("event_time"),
                row.get("event_name"),
                row.get("object_etag"),
                row.get("upload_grant_id"),
                row.get("source_system"),
                row.get("received_at"),
                row.get("dedupe_key"),
            ),
        )

    def get_source_event_by_dedupe_key(self, dedupe_key: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM source_object_events WHERE dedupe_key = %s",
            (dedupe_key,),
        ).fetchone()
        return dict(row) if row else None

