from __future__ import annotations

import json
import subprocess


def test_usage_report_cli_exposes_deviation_fields(usage_cli_env):
    completed = subprocess.run(
        ["python3", "-m", "faturama.cli", "usage-report"],
        check=True,
        capture_output=True,
        text=True,
        env=usage_cli_env,
    )

    payload = json.loads(completed.stdout)
    deviation = payload["deviations"][0]
    assert "criticality" in deviation
    assert "expected_statement" in deviation
    assert "observed_statement" in deviation
