from __future__ import annotations

import json
import subprocess


def test_process_invoice_cli_returns_contract(invoice_dir, cli_env):
    completed = subprocess.run(
        [
            "python3",
            "-m",
            "faturama.cli",
            "process-invoice",
            "--pdf-path",
            str(invoice_dir / "invoice-2026-04.pdf"),
            "--user-id",
            "demo-user",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=cli_env,
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] in {"parsed", "review_required"}
    assert payload["transactions_persisted"] == 3
