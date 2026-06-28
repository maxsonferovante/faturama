"""Repository analysis for scoped targets."""

from __future__ import annotations

from faturama.application.ports.repository_inspector import RepositoryInspector
from faturama.application.services.evidence_collector import build_evidence
from faturama.domain.entities.analysis_target import AnalysisTarget
from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.value_objects.evidence_kind import EvidenceKind


SOURCE_SUFFIXES = (".py", ".md", ".toml")
ANALYSIS_FEATURE_MARKERS = (
    "src/faturama/application/services/analysis_catalog.py",
    "src/faturama/application/services/repository_analysis.py",
    "src/faturama/application/use_cases/generate_usage_report.py",
    "src/faturama/interface/cli/usage_report.py",
    "tests/contract/test_cli_usage_report",
    "tests/integration/test_usage_report",
    "tests/e2e/test_usage_report",
    "tests/unit/test_usage_",
    "tests/unit/test_safe_patch_planner.py",
    "tests/unit/test_remediation_policy.py",
    "tests/conftest.py",
)


def analyze_repository(
    repository: RepositoryInspector,
    targets: list[AnalysisTarget],
) -> dict[str, list[EvidenceRecord]]:
    return {target.target_id: _collect_target_evidences(repository, target) for target in targets}


def _collect_target_evidences(
    repository: RepositoryInspector,
    target: AnalysisTarget,
) -> list[EvidenceRecord]:
    if target.target_id == "langgraph-runtime":
        return _collect_langgraph_evidences(repository, target)
    if target.target_id == "opendataloader-runtime":
        return _collect_opendataloader_evidences(repository, target)
    if target.target_id == "workflow-checkpoints":
        return _collect_workflow_evidences(repository, target)
    if target.target_id == "sidecar-artifacts":
        return _collect_sidecar_evidences(repository, target)
    return []


def _collect_langgraph_evidences(repository: RepositoryInspector, target: AnalysisTarget) -> list[EvidenceRecord]:
    evidences: list[EvidenceRecord] = []
    for hit in repository.search("langgraph", (".toml",)):
        if hit.path == "pyproject.toml":
            evidences.append(build_evidence(target.target_id, EvidenceKind.DECLARED_DEPENDENCY, hit, 0.95))
    for needle in ("from langgraph", "import langgraph", "StateGraph", "compile()", "workflow.compile("):
        for hit in repository.search(needle, (".py",)):
            if _is_usage_report_path(hit.path):
                continue
            evidences.append(build_evidence(target.target_id, EvidenceKind.EXECUTABLE_USAGE, hit, 1.0))
    for hit in repository.search("langgraph", (".md",)):
        if not _is_expectation_doc(hit.path):
            continue
        evidences.append(build_evidence(target.target_id, EvidenceKind.DOCUMENTATION_EXPECTATION, hit, 0.55))
    return deduplicate_evidences(evidences)


def _collect_opendataloader_evidences(repository: RepositoryInspector, target: AnalysisTarget) -> list[EvidenceRecord]:
    evidences: list[EvidenceRecord] = []
    for hit in repository.search("opendataloader-pdf", (".toml",)):
        if hit.path == "pyproject.toml":
            evidences.append(build_evidence(target.target_id, EvidenceKind.DECLARED_DEPENDENCY, hit, 0.95))
    for needle in ("import opendataloader", "import opendataloader_pdf", "opendataloader_pdf.", "convert("):
        for hit in repository.search(needle, (".py",)):
            if _is_usage_report_path(hit.path):
                continue
            kind = EvidenceKind.EXECUTABLE_USAGE if "refinamento-faturama/" not in hit.path else EvidenceKind.NAMING_ONLY
            confidence = 1.0 if kind is EvidenceKind.EXECUTABLE_USAGE else 0.3
            evidences.append(build_evidence(target.target_id, kind, hit, confidence))
    for hit in repository.search("opendataloader", SOURCE_SUFFIXES):
        if _is_usage_report_path(hit.path):
            continue
        if hit.path.startswith("src/faturama/infrastructure/opendataloader/"):
            evidences.append(build_evidence(target.target_id, EvidenceKind.NAMING_ONLY, hit, 0.45))
        elif _is_expectation_doc(hit.path):
            evidences.append(build_evidence(target.target_id, EvidenceKind.DOCUMENTATION_EXPECTATION, hit, 0.5))
    return deduplicate_evidences(evidences)


def _collect_workflow_evidences(repository: RepositoryInspector, target: AnalysisTarget) -> list[EvidenceRecord]:
    evidences: list[EvidenceRecord] = []
    for needle in ("WorkflowBuilder", "workflow_checkpoints", "checkpoint_store", "SQLiteCheckpointStore"):
        for hit in repository.search(needle, (".py",)):
            if _is_usage_report_path(hit.path):
                continue
            evidences.append(build_evidence(target.target_id, EvidenceKind.EXECUTION_SIGNAL, hit, 0.9))
    for hit in repository.search("checkpoint", (".md",)):
        if _is_expectation_doc(hit.path):
            evidences.append(build_evidence(target.target_id, EvidenceKind.DOCUMENTATION_EXPECTATION, hit, 0.4))
    return deduplicate_evidences(evidences)


def _collect_sidecar_evidences(repository: RepositoryInspector, target: AnalysisTarget) -> list[EvidenceRecord]:
    evidences: list[EvidenceRecord] = []
    for needle in ("resolve_runtime_artifact_paths", "require_artifacts", "raw_markdown_path", "raw_json_path"):
        for hit in repository.search(needle, SOURCE_SUFFIXES):
            if _is_usage_report_path(hit.path):
                continue
            kind = EvidenceKind.EXECUTION_SIGNAL if hit.path.startswith("src/") else EvidenceKind.DOCUMENTATION_EXPECTATION
            confidence = 0.9 if kind is EvidenceKind.EXECUTION_SIGNAL else 0.4
            evidences.append(build_evidence(target.target_id, kind, hit, confidence))
    for hit in repository.search("fallback", SOURCE_SUFFIXES):
        if _is_usage_report_path(hit.path):
            continue
        line = hit.line_text.lower()
        if "legacy fallback" in line or "fallback legado" in line:
            evidences.append(build_evidence(target.target_id, EvidenceKind.DOCUMENTATION_EXPECTATION, hit, 0.25))
    return deduplicate_evidences(evidences)


def deduplicate_evidences(evidences: list[EvidenceRecord]) -> list[EvidenceRecord]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[EvidenceRecord] = []
    for evidence in evidences:
        key = (evidence.target_id, evidence.evidence_kind.value, evidence.source_line_reference)
        if key in seen:
            continue
        seen.add(key)
        unique.append(evidence)
    return unique


def _is_usage_report_path(path: str) -> bool:
    return any(marker in path for marker in ANALYSIS_FEATURE_MARKERS)


def _is_expectation_doc(path: str) -> bool:
    return path == "README.md" or path.startswith("specs/001-invoice-extractor/") or path.startswith(
        "refinamento-faturama/"
    )
