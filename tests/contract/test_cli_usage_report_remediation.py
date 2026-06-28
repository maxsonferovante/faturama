from __future__ import annotations

import json
import subprocess


def test_usage_report_cli_reports_remediation_fields(usage_cli_env):
    completed = subprocess.run(
        ["python3", "-m", "faturama.cli", "usage-report", "--fix-when-safe"],
        check=True,
        capture_output=True,
        text=True,
        env=usage_cli_env,
    )

    payload = json.loads(completed.stdout)
    remediation = payload["remediations"][0]
    assert "action_status" in remediation
    assert "action_type" in remediation
    assert payload["auto_fixes_applied"] >= 1
