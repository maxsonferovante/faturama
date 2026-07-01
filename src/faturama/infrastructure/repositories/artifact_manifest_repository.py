from __future__ import annotations

from typing import Any


class ArtifactManifestRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def upsert_manifest(self, payload: dict[str, Any]) -> None:
        row = dict(payload)
        self.connection.execute(
            """
            INSERT INTO artifact_manifests (
                artifact_manifest_id, processing_id, artifact_bucket, source_pdf_uri, markdown_uri, json_uri,
                result_uri, artifact_key_prefix, artifact_status, checksum, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (processing_id) DO UPDATE SET
                artifact_manifest_id = EXCLUDED.artifact_manifest_id,
                artifact_bucket = EXCLUDED.artifact_bucket,
                source_pdf_uri = EXCLUDED.source_pdf_uri,
                markdown_uri = EXCLUDED.markdown_uri,
                json_uri = EXCLUDED.json_uri,
                result_uri = EXCLUDED.result_uri,
                artifact_key_prefix = EXCLUDED.artifact_key_prefix,
                artifact_status = EXCLUDED.artifact_status,
                checksum = EXCLUDED.checksum,
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at
            """,
            (
                row.get("artifact_manifest_id"),
                row.get("processing_id"),
                row.get("artifact_bucket"),
                row.get("source_pdf_uri"),
                row.get("markdown_uri"),
                row.get("json_uri"),
                row.get("result_uri"),
                row.get("artifact_key_prefix"),
                row.get("artifact_status"),
                row.get("checksum"),
                row.get("created_at"),
                row.get("updated_at"),
            ),
        )

    def get_by_processing_id(self, processing_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM artifact_manifests WHERE processing_id = %s",
            (processing_id,),
        ).fetchone()
        return dict(row) if row else None

