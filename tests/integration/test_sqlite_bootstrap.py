from __future__ import annotations

from faturama.infrastructure.database.sqlite import connect


def test_sqlite_bootstrap_creates_core_tables(temp_db):
    connection = connect(temp_db)
    names = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    assert {"documents", "statements", "transactions", "installment_plans", "projections", "summaries", "review_items", "decision_records"} <= names
