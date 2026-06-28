"""Expected behavior extraction from active specs and plan."""

from __future__ import annotations

from faturama.application.ports.repository_inspector import RepositoryInspector
from faturama.application.services.evidence_collector import build_evidence
from faturama.domain.entities.analysis_target import AnalysisTarget
from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.value_objects.evidence_kind import EvidenceKind


EXPECTATION_PATHS = (
    "specs/001-invoice-extractor/spec.md",
    "specs/001-invoice-extractor/plan.md",
    "README.md",
)


def load_expectations(
    repository: RepositoryInspector,
    targets: list[AnalysisTarget],
) -> dict[str, list[EvidenceRecord]]:
    expectations: dict[str, list[EvidenceRecord]] = {target.target_id: [] for target in targets}
    for target in targets:
        for marker in target.expected_markers:
            hits = repository.search(marker, (".md", ".toml"))
            for hit in hits:
                if hit.path not in EXPECTATION_PATHS and not hit.path.startswith("specs/001-invoice-extractor/"):
                    continue
                expectations[target.target_id].append(
                    build_evidence(target.target_id, EvidenceKind.DOCUMENTATION_EXPECTATION, hit, 0.5)
                )
    return expectations
