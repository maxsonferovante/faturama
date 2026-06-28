"""Document identity and hashing."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path


def build_document_id(seed: str | None = None) -> str:
    if seed:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"document:{seed}"))
    return str(uuid.uuid4())


def hash_file(pdf_path: str) -> str:
    digest = hashlib.sha256()
    with Path(pdf_path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_hash(*parts: object) -> str:
    payload = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
