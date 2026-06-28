from __future__ import annotations

from faturama.application.use_cases.generate_usage_report import generate_usage_report


def test_usage_report_generation_scans_targets_and_materializes_markdown(usage_report_repo):
    report = generate_usage_report(repository_root=str(usage_report_repo))

    assert report.targets_analyzed == 4
    assert report.findings == 4
    assert report.markdown_output_path is not None
    assert len(report.target_results) == 4
