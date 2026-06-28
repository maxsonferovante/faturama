"""Analysis target entity."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AnalysisTarget:
    target_id: str
    target_name: str
    target_kind: str
    scope_group: str
    expected_behavior: str
    analysis_status: str = "pending"
    expected_markers: tuple[str, ...] = field(default_factory=tuple)
