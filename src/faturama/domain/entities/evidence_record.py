"""Evidence record entity."""

from __future__ import annotations

from dataclasses import dataclass

from faturama.domain.value_objects.evidence_kind import EvidenceKind


@dataclass(slots=True)
class EvidenceRecord:
    evidence_id: str
    target_id: str
    evidence_kind: EvidenceKind
    source_path: str
    source_excerpt: str
    source_line_reference: str
    confidence_level: float
    observed_at: str
