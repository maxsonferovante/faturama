from __future__ import annotations

import json
import subprocess


def test_usage_report_e2e_generation_and_safe_fix(usage_cli_env, usage_report_repo):
    first = subprocess.run(
        ["python3", "-m", "faturama.cli", "usage-report"],
        check=True,
        capture_output=True,
        text=True,
        env=usage_cli_env,
    )
    second = subprocess.run(
        ["python3", "-m", "faturama.cli", "usage-report", "--fix-when-safe"],
        check=True,
        capture_output=True,
        text=True,
        env=usage_cli_env,
    )

    first_payload = json.loads(first.stdout)
    second_payload = json.loads(second.stdout)

    assert first_payload["targets_analyzed"] == 4
    assert second_payload["auto_fixes_applied"] >= 1
    assert (usage_report_repo / "docs/reports/usage-report.md").exists()
