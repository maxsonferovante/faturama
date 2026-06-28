"""Markdown materialization for usage reports."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from faturama.application.dto.usage_report_dto import UsageReportDTO
from faturama.application.ports.report_writer import ReportWriter


DEFAULT_OUTPUT_PATH = Path("docs/reports/usage-report.md")


class MarkdownUsageReportWriter(ReportWriter):
    def __init__(self, root: Path) -> None:
        self.root = root

    def write(self, report: UsageReportDTO, output_path: str | None = None) -> Path:
        target = self.root / Path(output_path or DEFAULT_OUTPUT_PATH)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_markdown(report), encoding="utf-8")
        return target


def render_markdown(report: UsageReportDTO) -> str:
    lines = [
        "# Relatório de Uso",
        "",
        "## Resumo Executivo",
        "",
        f"- Report ID: `{report.report_id}`",
        f"- Targets analyzed: `{report.targets_analyzed}`",
        f"- Findings: `{report.findings}`",
        f"- Critical deviations: `{report.critical_deviations}`",
        f"- Auto fixes applied: `{report.auto_fixes_applied}`",
        f"- Manual followups: `{report.manual_followups}`",
        "",
        "## Alvos Analisados",
        "",
    ]
    for finding in report.target_results:
        lines.extend(
            [
                f"### {finding.target_name}",
                "",
                f"- Classification: `{finding.classification}`",
                f"- Severity: `{finding.severity}`",
                f"- Summary: {finding.summary}",
                f"- Decision reason: {finding.decision_reason}",
                f"- Primary evidence: `{finding.primary_evidence.get('source_line_reference', '')}`",
                "",
            ]
        )
    lines.extend(["## Evidências", ""])
    for finding in report.target_results:
        evidence_items = [finding.primary_evidence, *finding.supporting_evidence]
        lines.append(f"### {finding.target_name}")
        lines.append("")
        for evidence in evidence_items:
            lines.append(
                f"- `{evidence.get('source_line_reference', '')}` [{evidence.get('evidence_kind', '')}]"
            )
        lines.append("")
    lines.extend(["## Desvios", ""])
    if report.deviations:
        for deviation in report.deviations:
            lines.extend(
                [
                    f"### {deviation['target_id']}",
                    "",
                    f"- Type: `{deviation['deviation_type']}`",
                    f"- Criticality: `{deviation['criticality']}`",
                    f"- Expected: {deviation['expected_statement']}",
                    f"- Observed: {deviation['observed_statement']}",
                    "",
                ]
            )
    else:
        lines.extend(["Nenhum desvio material identificado.", ""])
    lines.extend(["## Ações Corretivas ou Pendências Manuais", ""])
    if report.remediations:
        for remediation in report.remediations:
            payload = asdict(remediation)
            lines.extend(
                [
                    f"### {payload['target_id']}",
                    "",
                    f"- Action: `{payload['action_type']}`",
                    f"- Status: `{payload['action_status']}`",
                    f"- Summary: {payload['action_summary']}",
                    "",
                ]
            )
    else:
        lines.extend(["Nenhuma ação corretiva necessária.", ""])
    return "\n".join(lines)
