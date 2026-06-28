from __future__ import annotations

from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.services.usage_classifier import classify_usage
from faturama.domain.value_objects.evidence_kind import EvidenceKind
from faturama.domain.value_objects.usage_classification import UsageClassification


def _evidence(kind: EvidenceKind) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=f"e-{kind.value}",
        target_id="target",
        evidence_kind=kind,
        source_path="file.py",
        source_excerpt="snippet",
        source_line_reference="file.py:1",
        confidence_level=1.0,
        observed_at="now",
    )


def test_classify_usage_as_runtime_when_executable_evidence_exists():
    classification, _ = classify_usage([_evidence(EvidenceKind.EXECUTABLE_USAGE)])
    assert classification is UsageClassification.USED_IN_RUNTIME


def test_classify_usage_as_declared_not_used_when_only_dependency_exists():
    classification, _ = classify_usage([_evidence(EvidenceKind.DECLARED_DEPENDENCY)])
    assert classification is UsageClassification.DECLARED_NOT_USED


def test_classify_usage_as_conceptual_only_when_only_docs_exist():
    classification, _ = classify_usage([_evidence(EvidenceKind.DOCUMENTATION_EXPECTATION)])
    assert classification is UsageClassification.CONCEPTUAL_ONLY
