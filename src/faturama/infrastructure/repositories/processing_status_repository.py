"""Repository for the async status read model."""

from __future__ import annotations

from sqlite3 import Connection
from typing import Any


class ProcessingStatusRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def upsert_status(self, payload: dict[str, Any]) -> None:
        row = dict(payload)
        self.connection.execute(
            """
            INSERT OR REPLACE INTO processing_status_read_model (
                processing_id, document_id, file_hash, current_status, is_terminal, status_detail,
                result_reference, artifact_manifest_id, review_required, last_transition_at, updated_at
            ) VALUES (
                :processing_id, :document_id, :file_hash, :current_status, :is_terminal, :status_detail,
                :result_reference, :artifact_manifest_id, :review_required, :last_transition_at, :updated_at
            )
            """,
            row,
        )
        self.connection.commit()

    def get_status(self, processing_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM processing_status_read_model WHERE processing_id = ?",
            (processing_id,),
        ).fetchone()
        return dict(row) if row else None

    def list_by_file_hash(self, file_hash: str) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            "SELECT * FROM processing_status_read_model WHERE file_hash = ? ORDER BY updated_at DESC",
            (file_hash,),
        ).fetchall()
        return [dict(row) for row in rows]
