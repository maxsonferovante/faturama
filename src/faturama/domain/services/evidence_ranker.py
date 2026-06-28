"""Evidence ranking rules."""

from __future__ import annotations

from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.value_objects.evidence_kind import EvidenceKind


_WEIGHTS = {
    EvidenceKind.EXECUTABLE_USAGE: 100,
    EvidenceKind.EXECUTION_SIGNAL: 90,
    EvidenceKind.REINFORCING_TEST: 70,
    EvidenceKind.DECLARED_DEPENDENCY: 50,
    EvidenceKind.STRUCTURAL_SIGNAL: 40,
    EvidenceKind.DOCUMENTATION_EXPECTATION: 30,
    EvidenceKind.NAMING_ONLY: 20,
}


def rank_evidences(evidences: list[EvidenceRecord]) -> list[EvidenceRecord]:
    return sorted(
        evidences,
        key=lambda item: (_WEIGHTS[item.evidence_kind], item.confidence_level, item.source_line_reference),
        reverse=True,
    )
