"""Use case for the usage report feature."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
import os
from pathlib import Path
import uuid

from faturama.application.dto.usage_report_dto import UsageReportDTO
from faturama.application.services.analysis_catalog import build_analysis_catalog
from faturama.application.services.deviation_reporting import serialize_deviation
from faturama.application.services.expectation_loader import load_expectations
from faturama.application.services.finding_builder import build_finding
from faturama.application.services.remediation_reporting import build_remediation_dto
from faturama.application.services.repository_analysis import analyze_repository
from faturama.application.services.safe_patch_planner import plan_safe_patch
from faturama.domain.services.deviation_detector import detect_deviation
from faturama.domain.services.remediation_policy import manual_followup_action
from faturama.infrastructure.files.repository_reader import LocalRepositoryReader
from faturama.infrastructure.files.usage_report_remediator import FileRemediationService
from faturama.infrastructure.files.usage_report_writer import MarkdownUsageReportWriter
from faturama.observability.logging import get_logger
from faturama.observability.metrics import MetricsRegistry


def generate_usage_report(
    output_path: str | None = None,
    fix_when_safe: bool = False,
    repository_root: str | None = None,
) -> UsageReportDTO:
    root = _resolve_repository_root(repository_root)
    logger = get_logger("faturama.usage_report")
    metrics = MetricsRegistry()
    repository = LocalRepositoryReader(root)
    writer = MarkdownUsageReportWriter(root)
    remediator = FileRemediationService(root)
    report_id = str(uuid.uuid4())
    logger.info(
        "usage_report_started",
        extra={"event": "usage_report_started", "report_id": report_id, "repository_root": str(root)},
    )

    targets = build_analysis_catalog()
    evidence_map = analyze_repository(repository, targets)
    expectation_map = load_expectations(repository, targets)
    findings_dto = []
    findings = []
    deviations = []
    remediation_entities = []

    metrics.inc("targets_analyzed", len(targets))

    for target in targets:
        finding, finding_dto = build_finding(target, evidence_map[target.target_id])
        findings.append(finding)
        findings_dto.append(finding_dto)
        deviation = detect_deviation(target, finding, expectation_map[target.target_id])
        if deviation is None:
            continue
        deviations.append(deviation)
        if deviation.criticality.value == "high":
            metrics.inc("critical_deviations")
        planned = plan_safe_patch(repository, target, deviation, expectation_map[target.target_id])
        if planned:
            deviation.is_fixable_automatically = True
            remediation_entities.append(planned)
        else:
            remediation_entities.append(
                manual_followup_action(
                    deviation,
                    f"Revisar manualmente {target.target_name}: {deviation.observed_statement}",
                )
            )

    if fix_when_safe:
        remediation_entities = remediator.apply(remediation_entities)

    auto_fixes = sum(1 for action in remediation_entities if action.action_status == "applied")
    manual_followups = sum(1 for action in remediation_entities if action.requires_manual_followup)
    metrics.inc("auto_fixes_applied", auto_fixes)
    metrics.inc("manual_followups", manual_followups)

    report = UsageReportDTO(
        report_id=report_id,
        generated_at=datetime.now(UTC).isoformat(),
        repository_root=str(root),
        markdown_output_path=None,
        targets_analyzed=len(targets),
        findings=len(findings),
        critical_deviations=sum(1 for item in deviations if item.criticality.value == "high"),
        auto_fixes_applied=auto_fixes,
        manual_followups=manual_followups,
        operational_metrics=metrics.dump(),
        target_results=findings_dto,
        deviations=[serialize_deviation(item) for item in deviations],
        remediations=[
            build_remediation_dto(action, _target_id_for_deviation(action.deviation_id, deviations))
            for action in remediation_entities
        ],
    )
    markdown_path = writer.write(report, output_path)
    report.markdown_output_path = str(markdown_path)
    logger.info(
        "usage_report_completed",
        extra={
            "event": "usage_report_completed",
            "report_id": report.report_id,
            "metrics": report.operational_metrics,
            "markdown_output_path": report.markdown_output_path,
        },
    )
    return report


def report_to_payload(report: UsageReportDTO) -> dict[str, object]:
    payload = asdict(report)
    payload["target_results"] = [asdict(item) for item in report.target_results]
    payload["remediations"] = [asdict(item) for item in report.remediations]
    return payload


def _resolve_repository_root(repository_root: str | None) -> Path:
    env_override = os.getenv("FATURAMA_USAGE_REPORT_ROOT")
    if repository_root:
        return Path(repository_root).resolve()
    if env_override:
        return Path(env_override).resolve()
    return Path.cwd().resolve()


def _target_id_for_deviation(deviation_id: str, deviations: list) -> str:
    for deviation in deviations:
        if deviation.deviation_id == deviation_id:
            return deviation.target_id
    return "unknown"
