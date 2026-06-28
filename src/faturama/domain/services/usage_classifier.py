"""Rules to classify runtime usage."""

from __future__ import annotations

from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.value_objects.evidence_kind import EvidenceKind
from faturama.domain.value_objects.usage_classification import UsageClassification


def classify_usage(evidences: list[EvidenceRecord]) -> tuple[UsageClassification, str]:
    kinds = {evidence.evidence_kind for evidence in evidences}
    if EvidenceKind.EXECUTABLE_USAGE in kinds or EvidenceKind.EXECUTION_SIGNAL in kinds:
        return UsageClassification.USED_IN_RUNTIME, "Há evidência executável ou sinal direto de runtime."
    if EvidenceKind.DECLARED_DEPENDENCY in kinds:
        return UsageClassification.DECLARED_NOT_USED, "O componente aparece como dependência declarada sem prova de uso executável."
    if EvidenceKind.NAMING_ONLY in kinds or EvidenceKind.DOCUMENTATION_EXPECTATION in kinds:
        return UsageClassification.CONCEPTUAL_ONLY, "Há apenas naming, documentação ou expectativa arquitetural."
    return UsageClassification.INSUFFICIENT_CONTEXT, "Não há evidência suficiente para concluir o uso real."
