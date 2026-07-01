"""Transaction repository implementation."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from faturama.domain.entities.transaction_line import TransactionLine


class TransactionRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def save_transaction(self, transaction: TransactionLine) -> None:
        payload = asdict(transaction)
        columns = list(payload.keys())
        values = tuple(payload[column] for column in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        self.connection.execute(
            f"""
            INSERT INTO transactions ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT (transaction_id) DO UPDATE SET
                statement_id = EXCLUDED.statement_id,
                document_id = EXCLUDED.document_id,
                card_fingerprint = EXCLUDED.card_fingerprint,
                description_raw = EXCLUDED.description_raw,
                amount = EXCLUDED.amount,
                transaction_kind = EXCLUDED.transaction_kind,
                line_hash = EXCLUDED.line_hash,
                parse_confidence = EXCLUDED.parse_confidence,
                review_status = EXCLUDED.review_status,
                decision_state = EXCLUDED.decision_state,
                source_evidence_id = EXCLUDED.source_evidence_id,
                source_strategy = EXCLUDED.source_strategy,
                currency = EXCLUDED.currency,
                posted_date = EXCLUDED.posted_date,
                purchase_date = EXCLUDED.purchase_date,
                description_normalized = EXCLUDED.description_normalized,
                merchant_normalized = EXCLUDED.merchant_normalized,
                raw_text = EXCLUDED.raw_text,
                page_number = EXCLUDED.page_number,
                is_installment = EXCLUDED.is_installment,
                installment_current = EXCLUDED.installment_current,
                installment_total = EXCLUDED.installment_total
            """,
            values,
        )

    def list_by_statement(
        self,
        statement_id: str,
        kind: str | None = None,
        installments_only: bool = False,
        review_status: str | None = None,
    ) -> list[dict]:
        query = "SELECT * FROM transactions WHERE statement_id = %s"
        params: list[object] = [statement_id]
        if kind:
            query += " AND transaction_kind = %s"
            params.append(kind)
        if installments_only:
            query += " AND is_installment = TRUE"
        if review_status:
            query += " AND review_status = %s"
            params.append(review_status)
        query += " ORDER BY COALESCE(posted_date, purchase_date), transaction_id"
        rows = self.connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]

    def list_by_month(
        self,
        user_id: str,
        year: int,
        month: int,
        kind: str | None = None,
        card_fingerprint: str | None = None,
    ) -> list[dict]:
        query = """
            SELECT t.*
            FROM transactions t
            JOIN statements s ON s.statement_id = t.statement_id
            WHERE s.user_id = %s AND s.billing_year = %s AND s.billing_month = %s
              AND s.legacy_status != 'invalidated'
        """
        params: list[object] = [user_id, year, month]
        if kind:
            query += " AND t.transaction_kind = %s"
            params.append(kind)
        if card_fingerprint:
            query += " AND t.card_fingerprint = %s"
            params.append(card_fingerprint)
        rows = self.connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]

    def find_by_line_hash(self, statement_id: str, line_hash_value: str) -> dict | None:
        row = self.connection.execute(
            "SELECT * FROM transactions WHERE statement_id = %s AND line_hash = %s",
            (statement_id, line_hash_value),
        ).fetchone()
        return dict(row) if row else None
