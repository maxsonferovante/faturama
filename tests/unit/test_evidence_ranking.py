from __future__ import annotations

from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.services.evidence_ranker import rank_evidences
from faturama.domain.value_objects.evidence_kind import EvidenceKind


def _evidence(kind: EvidenceKind, confidence: float) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=kind.value,
        target_id="target",
        evidence_kind=kind,
        source_path="file.py",
        source_excerpt="snippet",
        source_line_reference=f"file.py:{confidence}",
        confidence_level=confidence,
        observed_at="now",
    )


def test_rank_evidences_prioritizes_runtime_signals():
    ranked = rank_evidences(
        [
            _evidence(EvidenceKind.DOCUMENTATION_EXPECTATION, 0.5),
            _evidence(EvidenceKind.EXECUTABLE_USAGE, 0.9),
            _evidence(EvidenceKind.DECLARED_DEPENDENCY, 0.8),
        ]
    )
    assert ranked[0].evidence_kind is EvidenceKind.EXECUTABLE_USAGE
