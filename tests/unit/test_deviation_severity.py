from __future__ import annotations

from faturama.application.services.analysis_catalog import build_analysis_catalog
from faturama.application.services.finding_builder import build_finding
from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.value_objects.deviation_severity import DeviationSeverity
from faturama.domain.value_objects.evidence_kind import EvidenceKind


def test_build_finding_marks_declared_components_as_high_severity():
    target = build_analysis_catalog()[0]
    evidence = EvidenceRecord(
        evidence_id="dep",
        target_id=target.target_id,
        evidence_kind=EvidenceKind.DECLARED_DEPENDENCY,
        source_path="pyproject.toml",
        source_excerpt="langgraph",
        source_line_reference="pyproject.toml:1",
        confidence_level=1.0,
        observed_at="now",
    )
    finding, _ = build_finding(target, [evidence])
    assert finding.finding_severity is DeviationSeverity.HIGH
