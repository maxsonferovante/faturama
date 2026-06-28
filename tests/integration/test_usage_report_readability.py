from __future__ import annotations

from faturama.application.use_cases.generate_usage_report import generate_usage_report


def test_usage_report_markdown_contains_required_sections_in_order(usage_report_repo):
    report = generate_usage_report(repository_root=str(usage_report_repo))
    markdown = (usage_report_repo / "docs/reports/usage-report.md").read_text(encoding="utf-8")

    indices = [
        markdown.index("## Resumo Executivo"),
        markdown.index("## Alvos Analisados"),
        markdown.index("## Evidências"),
        markdown.index("## Desvios"),
        markdown.index("## Ações Corretivas ou Pendências Manuais"),
    ]
    assert report.markdown_output_path is not None
    assert indices == sorted(indices)
