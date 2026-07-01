"""Workflow checkpoint store port."""

from __future__ import annotations

from typing import Any, Protocol


class CheckpointStore(Protocol):
    def save(
        self,
        job_id: str,
        thread_id: str,
        node_name: str,
        state: dict[str, Any],
        checkpoint_status: str = "active",
        review_required: bool = False,
    ) -> str: ...

    def latest(self, job_id: str) -> dict[str, Any] | None: ...

    def mark_restored(self, checkpoint_id: str) -> None: ...
