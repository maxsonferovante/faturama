"""Port for async artifact manifest persistence."""

from __future__ import annotations

from typing import Any, Protocol


class ArtifactManifestRepositoryPort(Protocol):
    def upsert_manifest(self, payload: dict[str, Any]) -> None: ...

    def get_by_processing_id(self, processing_id: str) -> dict[str, Any] | None: ...
