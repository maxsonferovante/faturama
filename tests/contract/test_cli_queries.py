from __future__ import annotations

import json
import subprocess

from faturama.infrastructure.database.postgres import connect_from_dsn
from tests.integration.test_monthly_queries import require_postgres_dsn, reset_database


def test_query_clis_return_json(invoice_dir, cli_env, monkeypatch):
    dsn = require_postgres_dsn(monkeypatch)
    reset_database(dsn)
    env = dict(cli_env)
    env["FATURAMA_DB_DSN"] = dsn

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
        env=env,
    )

    spend = subprocess.run(
        ["python3", "-m", "faturama.cli", "monthly-spend", "--user-id", "demo-user", "--month", "2026-04"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    current = subprocess.run(
        ["python3", "-m", "faturama.cli", "current-installments", "--user-id", "demo-user", "--month", "2026-04"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    future = subprocess.run(
        ["python3", "-m", "faturama.cli", "future-installments", "--user-id", "demo-user", "--month", "2026-05"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    balance = subprocess.run(
        ["python3", "-m", "faturama.cli", "remaining-balance", "--user-id", "demo-user"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    assert json.loads(spend.stdout)[0]["new_purchase_total"] == "250.00"
    assert len(json.loads(current.stdout)) == 1
    assert len(json.loads(future.stdout)) == 1
    assert json.loads(balance.stdout)[0]["remaining_balance"] == "3383.12"


def test_query_clis_ignore_invalidated_legacy_history(cli_env, monkeypatch):
    dsn = require_postgres_dsn(monkeypatch)
    reset_database(dsn)
    env = dict(cli_env)
    env["FATURAMA_DB_DSN"] = dsn
    connection = connect_from_dsn(dsn)
    connection.execute(
        """
        INSERT INTO summaries (
            summary_id, user_id, card_fingerprint, issuer_name, card_label, billing_year, billing_month,
            statement_total_amount, new_purchase_total, installment_charge_total, invoice_financing_total,
            interest_and_fees_total, refund_total, future_installment_balance, next_cycle_installment_commitment,
            runtime_source, legacy_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "legacy-summary",
            "demo-user",
            "legacy:9999",
            "Legacy",
            "Legacy 9999",
            2026,
            4,
            "100.00",
            "100.00",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "legacy",
            "invalidated",
        ),
    )
    connection.commit()
    connection.close()

    spend = subprocess.run(
        ["python3", "-m", "faturama.cli", "monthly-spend", "--user-id", "demo-user", "--month", "2026-04"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    assert json.loads(spend.stdout) == []
