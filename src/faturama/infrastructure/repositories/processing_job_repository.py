from __future__ import annotations

import json
from typing import Any


class ProcessingJobRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def create_job(self, payload: dict[str, Any]) -> None:
        row = dict(payload)
        row.setdefault("dispatch_attempt", 1)
        row.setdefault("status_detail", None)
        row.setdefault("execution_arn", None)
        row.setdefault("document_id", None)
        row.setdefault("file_hash", None)
        row.setdefault("started_at", None)
        row.setdefault("finished_at", None)
        row.setdefault("failure_code", None)
        row.setdefault("failure_message", None)
        row.setdefault("runtime_environment", None)
        self.connection.execute(
            """
            INSERT INTO processing_jobs (
                processing_id, source_event_id, execution_arn, dispatch_attempt, current_status, status_detail,
                bucket_name, object_key, document_id, file_hash, requested_at, started_at, finished_at,
                failure_code, failure_message, runtime_environment
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (processing_id) DO UPDATE SET
                source_event_id = EXCLUDED.source_event_id,
                execution_arn = EXCLUDED.execution_arn,
                dispatch_attempt = EXCLUDED.dispatch_attempt,
                current_status = EXCLUDED.current_status,
                status_detail = EXCLUDED.status_detail,
                bucket_name = EXCLUDED.bucket_name,
                object_key = EXCLUDED.object_key,
                document_id = EXCLUDED.document_id,
                file_hash = EXCLUDED.file_hash,
                requested_at = EXCLUDED.requested_at,
                started_at = EXCLUDED.started_at,
                finished_at = EXCLUDED.finished_at,
                failure_code = EXCLUDED.failure_code,
                failure_message = EXCLUDED.failure_message,
                runtime_environment = EXCLUDED.runtime_environment
            """,
            (
                row.get("processing_id"),
                row.get("source_event_id"),
                row.get("execution_arn"),
                row.get("dispatch_attempt"),
                row.get("current_status"),
                row.get("status_detail"),
                row.get("bucket_name"),
                row.get("object_key"),
                row.get("document_id"),
                row.get("file_hash"),
                row.get("requested_at"),
                row.get("started_at"),
                row.get("finished_at"),
                row.get("failure_code"),
                row.get("failure_message"),
                row.get("runtime_environment"),
            ),
        )

    def get_job(self, processing_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM processing_jobs WHERE processing_id = %s",
            (processing_id,),
        ).fetchone()
        return dict(row) if row else None

    def update_job(self, processing_id: str, **fields: Any) -> None:
        if not fields:
            return
        assignments = ", ".join(f"{key} = %s" for key in fields)
        params = list(fields.values()) + [processing_id]
        self.connection.execute(
            f"UPDATE processing_jobs SET {assignments} WHERE processing_id = %s",
            tuple(params),
        )

    def record_lifecycle_event(self, payload: dict[str, Any]) -> None:
        row = dict(payload)
        row.setdefault("payload_json", "{}")
        if isinstance(row["payload_json"], dict):
            row["payload_json"] = json.dumps(row["payload_json"], ensure_ascii=False)
        self.connection.execute(
            """
            INSERT INTO processing_lifecycle_events (
                event_id, processing_id, event_name, status, status_detail, payload_json, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                row.get("event_id"),
                row.get("processing_id"),
                row.get("event_name"),
                row.get("status"),
                row.get("status_detail"),
                row.get("payload_json"),
                row.get("created_at"),
            ),
        )

