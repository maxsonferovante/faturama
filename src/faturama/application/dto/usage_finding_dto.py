"""DTOs for usage findings."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class UsageFindingDTO:
    target_id: str
    target_name: str
    classification: str
    summary: str
    severity: str
    primary_evidence: dict[str, str]
    supporting_evidence: list[dict[str, str]] = field(default_factory=list)
    decision_reason: str = ""
