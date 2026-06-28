"""Build usage findings from evidences."""

from __future__ import annotations

from dataclasses import asdict
import uuid

from faturama.application.dto.usage_finding_dto import UsageFindingDTO
from faturama.domain.entities.analysis_target import AnalysisTarget
from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.entities.usage_finding import UsageFinding
from faturama.domain.services.evidence_ranker import rank_evidences
from faturama.domain.services.usage_classifier import classify_usage
from faturama.domain.value_objects.deviation_severity import DeviationSeverity
from faturama.domain.value_objects.evidence_kind import EvidenceKind
from faturama.domain.value_objects.usage_classification import UsageClassification


def build_finding(
    target: AnalysisTarget,
    evidences: list[EvidenceRecord],
) -> tuple[UsageFinding, UsageFindingDTO]:
    ranked = rank_evidences(evidences)
    classification, decision_reason = classify_usage(ranked)
    primary = ranked[0] if ranked else _empty_evidence(target.target_id)
    severity = _severity_for_classification(classification)
    summary = _summary_for_target(target, classification)
    finding = UsageFinding(
        finding_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"finding:{target.target_id}:{classification.value}")),
        target_id=target.target_id,
        usage_classification=classification,
        summary=summary,
        primary_evidence_id=primary.evidence_id,
        supporting_evidence_ids=tuple(item.evidence_id for item in ranked[1:]),
        decision_reason=decision_reason,
        finding_severity=severity,
    )
    dto = UsageFindingDTO(
        target_id=target.target_id,
        target_name=target.target_name,
        classification=classification.value,
        summary=summary,
        severity=severity.value,
        primary_evidence=_serialize_evidence(primary),
        supporting_evidence=[_serialize_evidence(item) for item in ranked[1:]],
        decision_reason=decision_reason,
    )
    return finding, dto


def _summary_for_target(target: AnalysisTarget, classification: UsageClassification) -> str:
    if classification is UsageClassification.USED_IN_RUNTIME:
        return f"{target.target_name} possui evidência concreta de uso no runtime atual."
    if classification is UsageClassification.DECLARED_NOT_USED:
        return f"{target.target_name} aparece como promessa ou dependência declarada, mas sem uso executável."
    if classification is UsageClassification.CONCEPTUAL_ONLY:
        return f"{target.target_name} aparece apenas em naming, documentação ou estrutura conceitual."
    return f"{target.target_name} não possui evidência suficiente para uma conclusão forte."


def _severity_for_classification(classification: UsageClassification) -> DeviationSeverity:
    if classification is UsageClassification.USED_IN_RUNTIME:
        return DeviationSeverity.LOW
    if classification is UsageClassification.INSUFFICIENT_CONTEXT:
        return DeviationSeverity.MEDIUM
    return DeviationSeverity.HIGH


def _serialize_evidence(evidence: EvidenceRecord) -> dict[str, str]:
    payload = asdict(evidence)
    payload["evidence_kind"] = evidence.evidence_kind.value
    return {key: str(value) for key, value in payload.items()}


def _empty_evidence(target_id: str) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"evidence:{target_id}:empty")),
        target_id=target_id,
        evidence_kind=EvidenceKind.NAMING_ONLY,
        source_path="",
        source_excerpt="",
        source_line_reference="",
        confidence_level=0.0,
        observed_at="",
    )
