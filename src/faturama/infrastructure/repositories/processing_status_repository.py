from __future__ import annotations

from typing import Any


class ProcessingStatusRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def upsert_status(self, payload: dict[str, Any]) -> None:
        row = dict(payload)
        self.connection.execute(
            """
            INSERT INTO processing_status_read_model (
                processing_id, document_id, file_hash, current_status, is_terminal, status_detail,
                result_reference, artifact_manifest_id, review_required, last_transition_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (processing_id) DO UPDATE SET
                document_id = EXCLUDED.document_id,
                file_hash = EXCLUDED.file_hash,
                current_status = EXCLUDED.current_status,
                is_terminal = EXCLUDED.is_terminal,
                status_detail = EXCLUDED.status_detail,
                result_reference = EXCLUDED.result_reference,
                artifact_manifest_id = EXCLUDED.artifact_manifest_id,
                review_required = EXCLUDED.review_required,
                last_transition_at = EXCLUDED.last_transition_at,
                updated_at = EXCLUDED.updated_at
            """,
            (
                row.get("processing_id"),
                row.get("document_id"),
                row.get("file_hash"),
                row.get("current_status"),
                row.get("is_terminal"),
                row.get("status_detail"),
                row.get("result_reference"),
                row.get("artifact_manifest_id"),
                row.get("review_required"),
                row.get("last_transition_at"),
                row.get("updated_at"),
            ),
        )

    def get_status(self, processing_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM processing_status_read_model WHERE processing_id = %s",
            (processing_id,),
        ).fetchone()
        return dict(row) if row else None

    def list_by_file_hash(self, file_hash: str) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            "SELECT * FROM processing_status_read_model WHERE file_hash = %s ORDER BY updated_at DESC",
            (file_hash,),
        ).fetchall()
        return [dict(row) for row in rows]

