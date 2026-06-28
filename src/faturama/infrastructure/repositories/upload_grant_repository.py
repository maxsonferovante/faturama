"""Repository for signed upload grants and source events."""

from __future__ import annotations

import json
from sqlite3 import Connection
from typing import Any


class UploadGrantRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def upsert_grant(self, payload: dict[str, Any]) -> None:
        row = dict(payload)
        row.setdefault("trace_context", "{}")
        if isinstance(row["trace_context"], dict):
            row["trace_context"] = json.dumps(row["trace_context"], ensure_ascii=False)
        self.connection.execute(
            """
            INSERT OR REPLACE INTO upload_authorization_grants (
                upload_grant_id, authorized_bucket, authorized_object_key, granted_to, granted_by, granted_at,
                expires_at, upload_completed_at, grant_status, trace_context
            ) VALUES (
                :upload_grant_id, :authorized_bucket, :authorized_object_key, :granted_to, :granted_by, :granted_at,
                :expires_at, :upload_completed_at, :grant_status, :trace_context
            )
            """,
            row,
        )
        self.connection.commit()

    def mark_used(self, upload_grant_id: str, uploaded_at: str) -> None:
        self.connection.execute(
            """
            UPDATE upload_authorization_grants
            SET upload_completed_at = ?, grant_status = 'used'
            WHERE upload_grant_id = ?
            """,
            (uploaded_at, upload_grant_id),
        )
        self.connection.commit()

    def get_grant(self, upload_grant_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM upload_authorization_grants WHERE upload_grant_id = ?",
            (upload_grant_id,),
        ).fetchone()
        return dict(row) if row else None

    def save_source_event(self, payload: dict[str, Any]) -> None:
        row = dict(payload)
        self.connection.execute(
            """
            INSERT OR REPLACE INTO source_object_events (
                source_event_id, bucket_name, object_key, object_version, event_time, event_name, object_etag,
                upload_grant_id, source_system, received_at, dedupe_key
            ) VALUES (
                :source_event_id, :bucket_name, :object_key, :object_version, :event_time, :event_name, :object_etag,
                :upload_grant_id, :source_system, :received_at, :dedupe_key
            )
            """,
            row,
        )
        self.connection.commit()

    def get_source_event_by_dedupe_key(self, dedupe_key: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM source_object_events WHERE dedupe_key = ?",
            (dedupe_key,),
        ).fetchone()
        return dict(row) if row else None
