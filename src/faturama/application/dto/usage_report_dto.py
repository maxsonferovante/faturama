"""DTOs for the usage report feature."""

from __future__ import annotations

from dataclasses import dataclass, field

from faturama.application.dto.remediation_dto import RemediationDTO
from faturama.application.dto.usage_finding_dto import UsageFindingDTO


@dataclass(slots=True)
class UsageReportDTO:
    report_id: str
    generated_at: str
    repository_root: str
    markdown_output_path: str | None
    targets_analyzed: int
    findings: int
    critical_deviations: int
    auto_fixes_applied: int
    manual_followups: int
    operational_metrics: dict[str, int]
    target_results: list[UsageFindingDTO] = field(default_factory=list)
    deviations: list[dict[str, object]] = field(default_factory=list)
    remediations: list[RemediationDTO] = field(default_factory=list)
