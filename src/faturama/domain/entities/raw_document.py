"""Raw document entity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RawDocument:
    document_id: str
    user_id: str
    source_pdf_path: str
    file_hash: str
    raw_markdown_path: str | None = None
    raw_json_path: str | None = None
    issuer_hint: str | None = None
    detected_issuer: str | None = None
    layout_family: str | None = None
    extraction_version: str = "local-v1"
    page_count: int = 0
    runtime_source: str = "official"
    legacy_status: str = "active"
    partial_status: str = "complete"
