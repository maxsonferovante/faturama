"""Port for async processing job persistence."""

from __future__ import annotations

from typing import Any, Protocol


class ProcessingJobRepositoryPort(Protocol):
    def create_job(self, payload: dict[str, Any]) -> None: ...

    def get_job(self, processing_id: str) -> dict[str, Any] | None: ...

    def update_job(self, processing_id: str, **fields: Any) -> None: ...

    def record_lifecycle_event(self, payload: dict[str, Any]) -> None: ...
