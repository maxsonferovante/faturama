"""Processing status enum helpers."""

from __future__ import annotations

from enum import StrEnum


class ProcessingStatus(StrEnum):
    PENDING = "PENDING"
    DISPATCHING = "DISPATCHING"
    RUNNING = "RUNNING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"

    @property
    def is_terminal(self) -> bool:
        return self in {self.SUCCESS, self.PARTIAL, self.FAILED}

    @property
    def review_required(self) -> bool:
        return self == self.REVIEW_REQUIRED
