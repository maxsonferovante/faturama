"""Summary repository implementation."""

from __future__ import annotations

import uuid
from sqlite3 import Connection


class SummaryRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def upsert_summary(self, payload: dict) -> None:
        payload = dict(payload)
        payload.setdefault("summary_id", str(uuid.uuid4()))
        payload.setdefault("legacy_status", "active")
        self.connection.execute(
            """
            INSERT OR REPLACE INTO summaries (
                summary_id, user_id, card_fingerprint, issuer_name, card_label, billing_year, billing_month,
                statement_total_amount, new_purchase_total, installment_charge_total, invoice_financing_total,
                interest_and_fees_total, refund_total, future_installment_balance, next_cycle_installment_commitment,
                runtime_source, legacy_status
            ) VALUES (
                :summary_id, :user_id, :card_fingerprint, :issuer_name, :card_label, :billing_year, :billing_month,
                :statement_total_amount, :new_purchase_total, :installment_charge_total, :invoice_financing_total,
                :interest_and_fees_total, :refund_total, :future_installment_balance, :next_cycle_installment_commitment,
                :runtime_source, :legacy_status
            )
            """,
            payload,
        )
        self.connection.commit()

    def list_summaries(self, user_id: str, year: int, month: int) -> list[dict]:
        rows = self.connection.execute(
            """
            SELECT * FROM summaries
            WHERE user_id = ? AND billing_year = ? AND billing_month = ?
              AND legacy_status != 'invalidated'
            """,
            (user_id, year, month),
        ).fetchall()
        return [dict(row) for row in rows]

    def invalidate_legacy_history(self, user_id: str | None = None) -> None:
        query = "UPDATE summaries SET legacy_status = 'invalidated' WHERE runtime_source != 'official'"
        params: tuple[object, ...] = ()
        if user_id:
            query += " AND user_id = ?"
            params = (user_id,)
        self.connection.execute(query, params)
        self.connection.commit()
