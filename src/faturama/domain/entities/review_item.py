"""Review item entity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReviewItem:
    review_item_id: str
    user_id: str
    entity_type: str
    entity_id: str
    reason_code: str
    reason_detail: str
    confidence_threshold_snapshot: float
    severity: str = "medium"
    status: str = "open"
    resolution_note: str | None = None
