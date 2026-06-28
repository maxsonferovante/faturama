"""Usage finding entity."""

from __future__ import annotations

from dataclasses import dataclass, field

from faturama.domain.value_objects.deviation_severity import DeviationSeverity
from faturama.domain.value_objects.usage_classification import UsageClassification


@dataclass(slots=True)
class UsageFinding:
    finding_id: str
    target_id: str
    usage_classification: UsageClassification
    summary: str
    primary_evidence_id: str
    supporting_evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    decision_reason: str = ""
    finding_severity: DeviationSeverity = DeviationSeverity.LOW
