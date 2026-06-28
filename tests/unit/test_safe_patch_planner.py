from __future__ import annotations

from faturama.application.services.analysis_catalog import build_analysis_catalog
from faturama.application.services.evidence_collector import build_evidence
from faturama.application.services.safe_patch_planner import plan_safe_patch
from faturama.domain.entities.specification_deviation import SpecificationDeviation
from faturama.domain.value_objects.deviation_severity import DeviationSeverity
from faturama.domain.value_objects.evidence_kind import EvidenceKind
from faturama.infrastructure.files.repository_reader import LocalRepositoryReader


def test_plan_safe_patch_returns_patch_for_unique_markdown_excerpt(usage_report_repo):
    repository = LocalRepositoryReader(usage_report_repo)
    target = build_analysis_catalog()[0]
    hit = repository.search("LangGraph usado em runtime", (".md",))[0]
    evidence = build_evidence(target.target_id, EvidenceKind.DOCUMENTATION_EXPECTATION, hit, 0.5)
    deviation = SpecificationDeviation(
        deviation_id="dev-patch",
        target_id=target.target_id,
        expected_statement="expected",
        observed_statement="observed",
        deviation_type="type",
        criticality=DeviationSeverity.MEDIUM,
        is_fixable_automatically=True,
    )
    action = plan_safe_patch(repository, target, deviation, [evidence])
    assert action is not None
    assert action.patch_path == "README.md"
