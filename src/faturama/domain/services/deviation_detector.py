"""Deviation detection rules."""

from __future__ import annotations

import uuid

from faturama.domain.entities.analysis_target import AnalysisTarget
from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.entities.specification_deviation import SpecificationDeviation
from faturama.domain.entities.usage_finding import UsageFinding
from faturama.domain.value_objects.deviation_severity import DeviationSeverity
from faturama.domain.value_objects.usage_classification import UsageClassification


def detect_deviation(
    target: AnalysisTarget,
    finding: UsageFinding,
    expectation_evidences: list[EvidenceRecord],
) -> SpecificationDeviation | None:
    if finding.usage_classification is UsageClassification.USED_IN_RUNTIME:
        return None
    if not expectation_evidences:
        if finding.usage_classification is UsageClassification.INSUFFICIENT_CONTEXT:
            return _build_deviation(
                target,
                "Sem expectativa explícita para comparação.",
                "A análise não encontrou contexto suficiente para concluir o uso real.",
                "insufficient_evidence",
                DeviationSeverity.MEDIUM,
                False,
                [finding.primary_evidence_id],
            )
        return None

    if finding.usage_classification is UsageClassification.DECLARED_NOT_USED:
        return _build_deviation(
            target,
            target.expected_behavior,
            "O componente permanece apenas como dependência declarada, sem integração executável observável.",
            "declared_without_runtime",
            DeviationSeverity.HIGH,
            False,
            [finding.primary_evidence_id, *[item.evidence_id for item in expectation_evidences[:2]]],
        )
    if finding.usage_classification is UsageClassification.CONCEPTUAL_ONLY:
        return _build_deviation(
            target,
            target.expected_behavior,
            "O componente aparece apenas em naming, estrutura ou documentação, sem uso real confirmado.",
            "conceptual_without_runtime",
            DeviationSeverity.HIGH,
            False,
            [finding.primary_evidence_id, *[item.evidence_id for item in expectation_evidences[:2]]],
        )
    return _build_deviation(
        target,
        target.expected_behavior,
        "A análise permaneceu inconclusiva diante do contexto disponível.",
        "insufficient_context",
        DeviationSeverity.MEDIUM,
        False,
        [finding.primary_evidence_id, *[item.evidence_id for item in expectation_evidences[:2]]],
    )


def _build_deviation(
    target: AnalysisTarget,
    expected_statement: str,
    observed_statement: str,
    deviation_type: str,
    criticality: DeviationSeverity,
    is_fixable_automatically: bool,
    evidence_ids: list[str],
) -> SpecificationDeviation:
    return SpecificationDeviation(
        deviation_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"deviation:{target.target_id}:{deviation_type}")),
        target_id=target.target_id,
        expected_statement=expected_statement,
        observed_statement=observed_statement,
        deviation_type=deviation_type,
        criticality=criticality,
        is_fixable_automatically=is_fixable_automatically,
        rationale="Comparação entre expectativa documentada e comportamento observável do checkout atual.",
        evidence_ids=tuple(evidence_ids),
    )
