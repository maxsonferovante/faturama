from __future__ import annotations

import json
import subprocess


def test_usage_report_cli_returns_contract_shape(usage_cli_env, tmp_path):
    output_file = tmp_path / "usage.md"
    completed = subprocess.run(
        [
            "python3",
            "-m",
            "faturama.cli",
            "usage-report",
            "--output-file",
            str(output_file),
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=usage_cli_env,
    )

    payload = json.loads(completed.stdout)
    assert payload["report_id"]
    assert payload["targets_analyzed"] == 4
    assert "operational_metrics" in payload
    assert output_file.exists()
