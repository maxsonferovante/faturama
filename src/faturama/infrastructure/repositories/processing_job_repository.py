"""Repository for async processing jobs and lifecycle events."""

from __future__ import annotations

import json
from sqlite3 import Connection
from typing import Any


class ProcessingJobRepository:
    def __init__(self, connection: Connection) -> None:
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
            INSERT OR REPLACE INTO processing_jobs (
                processing_id, source_event_id, execution_arn, dispatch_attempt, current_status, status_detail,
                bucket_name, object_key, document_id, file_hash, requested_at, started_at, finished_at,
                failure_code, failure_message, runtime_environment
            ) VALUES (
                :processing_id, :source_event_id, :execution_arn, :dispatch_attempt, :current_status, :status_detail,
                :bucket_name, :object_key, :document_id, :file_hash, :requested_at, :started_at, :finished_at,
                :failure_code, :failure_message, :runtime_environment
            )
            """,
            row,
        )
        self.connection.commit()

    def get_job(self, processing_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM processing_jobs WHERE processing_id = ?",
            (processing_id,),
        ).fetchone()
        return dict(row) if row else None

    def update_job(self, processing_id: str, **fields: Any) -> None:
        if not fields:
            return
        assignments = ", ".join(f"{key} = :{key}" for key in fields)
        payload = dict(fields)
        payload["processing_id"] = processing_id
        self.connection.execute(
            f"UPDATE processing_jobs SET {assignments} WHERE processing_id = :processing_id",
            payload,
        )
        self.connection.commit()

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
                :event_id, :processing_id, :event_name, :status, :status_detail, :payload_json, :created_at
            )
            """,
            row,
        )
        self.connection.commit()
