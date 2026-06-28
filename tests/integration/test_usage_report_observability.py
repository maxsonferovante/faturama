from __future__ import annotations

import json
import subprocess

from faturama.application.use_cases.generate_usage_report import generate_usage_report


def test_usage_report_exposes_operational_metrics(usage_report_repo):
    report = generate_usage_report(repository_root=str(usage_report_repo))

    assert report.operational_metrics["targets_analyzed"] == 4
    assert "critical_deviations" in report.operational_metrics


def test_usage_report_cli_returns_structured_error_for_output_failures(usage_cli_env, usage_report_repo):
    blocked = usage_report_repo / "blocked"
    blocked.write_text("not-a-dir", encoding="utf-8")
    completed = subprocess.run(
        [
            "python3",
            "-m",
            "faturama.cli",
            "usage-report",
            "--output-file",
            "blocked/report.md",
        ],
        capture_output=True,
        text=True,
        env=usage_cli_env,
        check=False,
    )

    payload = json.loads(completed.stdout)
    assert completed.returncode == 1
    assert payload["error_code"] == "usage_report_failed"
