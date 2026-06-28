from __future__ import annotations

from pathlib import Path

from faturama.application.services.artifact_manifest_service import ArtifactManifestService
from faturama.infrastructure.aws.s3_storage import S3StorageAdapter
from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.artifact_manifest_repository import ArtifactManifestRepository


def test_artifact_manifest_is_persisted(async_settings, tmp_path):
    source = tmp_path / "invoice.pdf"
    source.write_bytes(b"%PDF-1.4 fake")
    markdown = tmp_path / "invoice.md"
    markdown.write_text("markdown", encoding="utf-8")
    raw_json = tmp_path / "invoice.json"
    raw_json.write_text("{}", encoding="utf-8")
    storage = S3StorageAdapter(root_dir=async_settings.artifact_cache_dir.parent / "object-store")
    repository = ArtifactManifestRepository(connect(async_settings.database_path))
    service = ArtifactManifestService(
        storage=storage,
        repository=repository,
        artifact_bucket=async_settings.artifact_bucket,
        artifact_prefix=async_settings.artifact_prefix,
    )
    manifest = service.persist(
        processing_id="evt-1",
        document_id="doc-1",
        source_pdf_path=source,
        markdown_path=markdown,
        json_path=raw_json,
        result_payload={"status": "SUCCESS"},
        source_object_key="incoming/invoice.pdf",
    )
    saved = repository.get_by_processing_id("evt-1")
    assert saved is not None
    assert saved["artifact_key_prefix"] == manifest["artifact_key_prefix"]
