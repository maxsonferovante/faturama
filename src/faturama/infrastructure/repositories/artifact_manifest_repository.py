"""Repository for async artifact manifests."""

from __future__ import annotations

from sqlite3 import Connection
from typing import Any


class ArtifactManifestRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def upsert_manifest(self, payload: dict[str, Any]) -> None:
        row = dict(payload)
        self.connection.execute(
            """
            INSERT OR REPLACE INTO artifact_manifests (
                artifact_manifest_id, processing_id, artifact_bucket, source_pdf_uri, markdown_uri, json_uri,
                result_uri, artifact_key_prefix, artifact_status, checksum, created_at, updated_at
            ) VALUES (
                :artifact_manifest_id, :processing_id, :artifact_bucket, :source_pdf_uri, :markdown_uri, :json_uri,
                :result_uri, :artifact_key_prefix, :artifact_status, :checksum, :created_at, :updated_at
            )
            """,
            row,
        )
        self.connection.commit()

    def get_by_processing_id(self, processing_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM artifact_manifests WHERE processing_id = ?",
            (processing_id,),
        ).fetchone()
        return dict(row) if row else None
