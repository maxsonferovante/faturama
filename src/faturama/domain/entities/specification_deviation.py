"""Specification deviation entity."""

from __future__ import annotations

from dataclasses import dataclass, field

from faturama.domain.value_objects.deviation_severity import DeviationSeverity


@dataclass(slots=True)
class SpecificationDeviation:
    deviation_id: str
    target_id: str
    expected_statement: str
    observed_statement: str
    deviation_type: str
    criticality: DeviationSeverity
    is_fixable_automatically: bool
    rationale: str = ""
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
