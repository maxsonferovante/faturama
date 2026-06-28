"""Deterministic artifact-key helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path


def build_artifact_key_prefix(*, artifact_prefix: str, processing_id: str, document_id: str | None, object_key: str) -> str:
    suffix_source = document_id or object_key
    digest = hashlib.sha256(suffix_source.encode("utf-8")).hexdigest()[:12]
    object_stem = Path(object_key).stem
    return f"{artifact_prefix.rstrip('/')}/{processing_id}/{object_stem}-{digest}"
