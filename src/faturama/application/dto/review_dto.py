"""Review DTOs."""

from __future__ import annotations

from faturama.shared.pydantic_compat import BaseModel


class ReviewItemDTO(BaseModel):
    review_item_id: str
    entity_type: str
    entity_id: str
    reason_code: str
    reason_detail: str
    confidence_threshold_snapshot: float
    status: str
