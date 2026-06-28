from __future__ import annotations

import json
import subprocess


def test_review_queue_and_resolve_review_contract(invoice_dir, cli_env):
    subprocess.run(
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
    queue = subprocess.run(
        ["python3", "-m", "faturama.cli", "review-queue", "--user-id", "demo-user"],
        check=True,
        capture_output=True,
        text=True,
        env=cli_env,
    )
    review_item = json.loads(queue.stdout)[0]
    resolved = subprocess.run(
        [
            "python3",
            "-m",
            "faturama.cli",
            "resolve-review",
            "--review-item-id",
            review_item["review_item_id"],
            "--resolution",
            "accepted",
            "--note",
            "Confirmado",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=cli_env,
    )
    assert json.loads(resolved.stdout)["status"] == "resolved"
