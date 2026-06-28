from __future__ import annotations

from faturama.application.use_cases.generate_usage_report import generate_usage_report


def test_usage_report_detects_declared_but_unused_integrations(usage_report_repo):
    report = generate_usage_report(repository_root=str(usage_report_repo))
    target_ids = {item["target_id"] for item in report.deviations}

    assert "langgraph-runtime" in target_ids
    assert "opendataloader-runtime" in target_ids
