"""Plan safe deterministic patches when possible."""

from __future__ import annotations

from faturama.application.ports.repository_inspector import RepositoryInspector
from faturama.domain.entities.analysis_target import AnalysisTarget
from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.entities.remediation_action import RemediationAction
from faturama.domain.entities.specification_deviation import SpecificationDeviation


def plan_safe_patch(
    repository: RepositoryInspector,
    target: AnalysisTarget,
    deviation: SpecificationDeviation,
    expectation_evidences: list[EvidenceRecord],
) -> RemediationAction | None:
    for evidence in expectation_evidences:
        if not evidence.source_path.endswith(".md"):
            continue
        file_text = repository.read_text(evidence.source_path)
        if file_text.count(evidence.source_excerpt) != 1:
            continue
        replacement = evidence.source_excerpt.replace(
            "usado",
            "declarado",
        )
        if replacement == evidence.source_excerpt:
            continue
        return RemediationAction(
            action_id=f"patch:{deviation.deviation_id}",
            deviation_id=deviation.deviation_id,
            action_type="safe_patch",
            action_status="planned",
            action_summary=f"Ajustar documentação de {target.target_name} para refletir o estado real observado.",
            change_targets=(evidence.source_path,),
            requires_manual_followup=False,
            patch_path=evidence.source_path,
            original_snippet=evidence.source_excerpt,
            replacement_snippet=replacement,
            details=f"Patch determinístico derivado de {evidence.source_line_reference}.",
        )
    return None
