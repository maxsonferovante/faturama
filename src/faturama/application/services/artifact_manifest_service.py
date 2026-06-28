"""Build and persist artifact manifests."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path

from faturama.application.services.artifact_key_builder import build_artifact_key_prefix


def _checksum(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        if path.exists():
            digest.update(path.read_bytes())
    return digest.hexdigest()


class ArtifactManifestService:
    def __init__(self, *, storage: object, repository: object, artifact_bucket: str, artifact_prefix: str) -> None:
        self.storage = storage
        self.repository = repository
        self.artifact_bucket = artifact_bucket
        self.artifact_prefix = artifact_prefix

    def persist(
        self,
        *,
        processing_id: str,
        document_id: str | None,
        source_pdf_path: Path,
        markdown_path: Path | None,
        json_path: Path | None,
        result_payload: dict[str, object],
        source_object_key: str,
    ) -> dict[str, object]:
        timestamp = datetime.now(UTC).isoformat()
        key_prefix = build_artifact_key_prefix(
            artifact_prefix=self.artifact_prefix,
            processing_id=processing_id,
            document_id=document_id,
            object_key=source_object_key,
        )
        result_path = source_pdf_path.parent / f"{source_pdf_path.stem}-result.json"
        result_path.write_text(json.dumps(result_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        source_key = f"{key_prefix}/{source_pdf_path.name}"
        markdown_key = f"{key_prefix}/{markdown_path.name}" if markdown_path else None
        json_key = f"{key_prefix}/{json_path.name}" if json_path else None
        result_key = f"{key_prefix}/{result_path.name}"

        manifest = {
            "artifact_manifest_id": processing_id,
            "processing_id": processing_id,
            "artifact_bucket": self.artifact_bucket,
            "source_pdf_uri": self.storage.upload_file(source_pdf_path, self.artifact_bucket, source_key),
            "markdown_uri": self.storage.upload_file(markdown_path, self.artifact_bucket, markdown_key) if markdown_path and markdown_key else None,
            "json_uri": self.storage.upload_file(json_path, self.artifact_bucket, json_key) if json_path and json_key else None,
            "result_uri": self.storage.upload_file(result_path, self.artifact_bucket, result_key),
            "artifact_key_prefix": key_prefix,
            "artifact_status": "generated",
            "checksum": _checksum([path for path in [source_pdf_path, markdown_path, json_path, result_path] if path]),
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        self.repository.upsert_manifest(manifest)
        return manifest
