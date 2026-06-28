"""Usage classification value object."""

from __future__ import annotations

from enum import StrEnum


class UsageClassification(StrEnum):
    USED_IN_RUNTIME = "used_in_runtime"
    DECLARED_NOT_USED = "declared_not_used"
    CONCEPTUAL_ONLY = "conceptual_only"
    INSUFFICIENT_CONTEXT = "insufficient_context"
