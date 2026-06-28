from __future__ import annotations

from faturama.application.use_cases.generate_usage_report import generate_usage_report


def test_usage_report_writer_materializes_markdown(usage_report_repo):
    report = generate_usage_report(repository_root=str(usage_report_repo))
    markdown = (usage_report_repo / "docs/reports/usage-report.md").read_text(encoding="utf-8")

    assert report.markdown_output_path is not None
    assert "## Resumo Executivo" in markdown
    assert "## Desvios" in markdown
