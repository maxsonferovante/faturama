from __future__ import annotations

from faturama.application.use_cases.generate_usage_report import generate_usage_report


def test_usage_report_applies_safe_fix_when_enabled(usage_report_repo):
    report = generate_usage_report(repository_root=str(usage_report_repo), fix_when_safe=True)
    readme = (usage_report_repo / "README.md").read_text(encoding="utf-8")

    assert report.auto_fixes_applied >= 1
    assert "declarado em runtime" in readme
