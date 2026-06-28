"""Decision record DTOs."""

from __future__ import annotations

from faturama.shared.pydantic_compat import BaseModel


class DecisionRecordDTO(BaseModel):
    decision_id: str
    entity_type: str
    entity_id: str
    decision_state: str
    confidence_structural: float
    confidence_semantic: float
    confidence_relational: float
    confidence_operational: float
    decision_reason: str
