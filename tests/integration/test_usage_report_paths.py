from __future__ import annotations

from pathlib import Path

from faturama.application.use_cases.generate_usage_report import generate_usage_report


def test_usage_report_creates_parent_directories_for_custom_output(usage_report_repo):
    output = Path("custom/reports/runtime.md")
    report = generate_usage_report(output_path=str(output), repository_root=str(usage_report_repo))

    assert report.markdown_output_path == str(usage_report_repo / output)
    assert (usage_report_repo / output).exists()
