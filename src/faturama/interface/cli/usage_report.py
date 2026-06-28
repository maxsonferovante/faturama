"""CLI command for usage report generation."""

from __future__ import annotations

from faturama.application.use_cases.generate_usage_report import generate_usage_report, report_to_payload
from faturama.observability.logging import get_logger


def _render_table(payload: dict[str, object]) -> str:
    return "\n".join(
        [
            "Relatório de Uso",
            f"report_id: {payload['report_id']}",
            f"targets_analyzed: {payload['targets_analyzed']}",
            f"findings: {payload['findings']}",
            f"critical_deviations: {payload['critical_deviations']}",
            f"auto_fixes_applied: {payload['auto_fixes_applied']}",
            f"manual_followups: {payload['manual_followups']}",
            f"markdown_output_path: {payload['markdown_output_path']}",
        ]
    )


def _handle_usage_report(args) -> dict[str, object] | str:
    logger = get_logger("faturama.usage_report.cli")
    try:
        report = generate_usage_report(
            output_path=args.output_file,
            fix_when_safe=args.fix_when_safe,
        )
        payload = report_to_payload(report)
        if args.format == "table":
            return _render_table(payload)
        return payload
    except Exception as exc:
        logger.exception(
            "usage_report_failed",
            extra={"event": "usage_report_failed", "error_code": "usage_report_failed"},
        )
        return {
            "error_code": "usage_report_failed",
            "message": str(exc),
        }, 1


def register_usage_report(subparsers) -> None:
    parser = subparsers.add_parser("usage-report")
    parser.add_argument("--output-file")
    parser.add_argument("--fix-when-safe", action="store_true")
    parser.add_argument("--format", choices=("json", "table"), default="json")
    parser.set_defaults(handler=_handle_usage_report)
