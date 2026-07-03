"""Summary repository implementation."""

from __future__ import annotations

import uuid
from typing import Any


class SummaryRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def upsert_summary(self, payload: dict) -> None:
        payload = dict(payload)
        payload.setdefault("summary_id", str(uuid.uuid4()))
        payload.setdefault("legacy_status", "active")
        self.connection.execute(
            """
            INSERT INTO summaries (
                summary_id, user_id, card_fingerprint, issuer_name, card_label, billing_year, billing_month,
                statement_total_amount, new_purchase_total, installment_charge_total, invoice_financing_total,
                interest_and_fees_total, refund_total, future_installment_balance, next_cycle_installment_commitment,
                runtime_source, legacy_status
            ) VALUES (
                %(summary_id)s, %(user_id)s, %(card_fingerprint)s, %(issuer_name)s, %(card_label)s, %(billing_year)s, %(billing_month)s,
                %(statement_total_amount)s, %(new_purchase_total)s, %(installment_charge_total)s, %(invoice_financing_total)s,
                %(interest_and_fees_total)s, %(refund_total)s, %(future_installment_balance)s, %(next_cycle_installment_commitment)s,
                %(runtime_source)s, %(legacy_status)s
            )
            ON CONFLICT (summary_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                card_fingerprint = EXCLUDED.card_fingerprint,
                issuer_name = EXCLUDED.issuer_name,
                card_label = EXCLUDED.card_label,
                billing_year = EXCLUDED.billing_year,
                billing_month = EXCLUDED.billing_month,
                statement_total_amount = EXCLUDED.statement_total_amount,
                new_purchase_total = EXCLUDED.new_purchase_total,
                installment_charge_total = EXCLUDED.installment_charge_total,
                invoice_financing_total = EXCLUDED.invoice_financing_total,
                interest_and_fees_total = EXCLUDED.interest_and_fees_total,
                refund_total = EXCLUDED.refund_total,
                future_installment_balance = EXCLUDED.future_installment_balance,
                next_cycle_installment_commitment = EXCLUDED.next_cycle_installment_commitment,
                runtime_source = EXCLUDED.runtime_source,
                legacy_status = EXCLUDED.legacy_status
            """,
            payload,
        )

    def list_summaries(self, user_id: str, year: int, month: int) -> list[dict]:
        rows = self.connection.execute(
            """
            SELECT * FROM summaries
            WHERE user_id = %s AND billing_year = %s AND billing_month = %s
              AND legacy_status != 'invalidated'
            """,
            (user_id, year, month),
        ).fetchall()
        return [dict(row) for row in rows]

    def invalidate_legacy_history(self, user_id: str | None = None) -> None:
        query = "UPDATE summaries SET legacy_status = 'invalidated' WHERE runtime_source != 'official'"
        params: tuple[object, ...] = ()
        if user_id:
            query += " AND user_id = %s"
            params = (user_id,)
        self.connection.execute(query, params)
