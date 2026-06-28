"""Transaction repository implementation."""

from __future__ import annotations

from dataclasses import asdict
from sqlite3 import Connection

from faturama.domain.entities.transaction_line import TransactionLine


class TransactionRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def save_transaction(self, transaction: TransactionLine) -> None:
        self.connection.execute(
            """
            INSERT OR REPLACE INTO transactions (
                transaction_id, statement_id, document_id, card_fingerprint, description_raw, amount,
                transaction_kind, line_hash, parse_confidence, review_status, decision_state,
                source_evidence_id, source_strategy, currency, posted_date, purchase_date,
                description_normalized, merchant_normalized, raw_text, page_number, is_installment,
                installment_current, installment_total
            ) VALUES (
                :transaction_id, :statement_id, :document_id, :card_fingerprint, :description_raw, :amount,
                :transaction_kind, :line_hash, :parse_confidence, :review_status, :decision_state,
                :source_evidence_id, :source_strategy, :currency, :posted_date, :purchase_date,
                :description_normalized, :merchant_normalized, :raw_text, :page_number, :is_installment,
                :installment_current, :installment_total
            )
            """,
            asdict(transaction),
        )
        self.connection.commit()

    def list_by_statement(
        self,
        statement_id: str,
        kind: str | None = None,
        installments_only: bool = False,
        review_status: str | None = None,
    ) -> list[dict]:
        query = "SELECT * FROM transactions WHERE statement_id = ?"
        params: list[object] = [statement_id]
        if kind:
            query += " AND transaction_kind = ?"
            params.append(kind)
        if installments_only:
            query += " AND is_installment = 1"
        if review_status:
            query += " AND review_status = ?"
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
            WHERE s.user_id = ? AND s.billing_year = ? AND s.billing_month = ?
              AND s.legacy_status != 'invalidated'
        """
        params: list[object] = [user_id, year, month]
        if kind:
            query += " AND t.transaction_kind = ?"
            params.append(kind)
        if card_fingerprint:
            query += " AND t.card_fingerprint = ?"
            params.append(card_fingerprint)
        rows = self.connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]

    def find_by_line_hash(self, statement_id: str, line_hash_value: str) -> dict | None:
        row = self.connection.execute(
            "SELECT * FROM transactions WHERE statement_id = ? AND line_hash = ?",
            (statement_id, line_hash_value),
        ).fetchone()
        return dict(row) if row else None
