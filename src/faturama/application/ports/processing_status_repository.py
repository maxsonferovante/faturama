"""Port for status read model persistence."""

from __future__ import annotations

from typing import Any, Protocol


class ProcessingStatusRepositoryPort(Protocol):
    def upsert_status(self, payload: dict[str, Any]) -> None: ...

    def get_status(self, processing_id: str) -> dict[str, Any] | None: ...

    def list_by_file_hash(self, file_hash: str) -> list[dict[str, Any]]: ...
