"""Statement repository implementation."""

from __future__ import annotations

from dataclasses import asdict
from sqlite3 import Connection
from typing import Iterable

from faturama.domain.entities.invoice_statement import InvoiceStatement
from faturama.domain.entities.raw_document import RawDocument


class StatementRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def save_document(self, document: RawDocument) -> None:
        self.connection.execute(
            """
            INSERT OR REPLACE INTO documents (
                document_id, user_id, source_pdf_path, file_hash, raw_markdown_path, raw_json_path,
                issuer_hint, detected_issuer, layout_family, extraction_version, page_count,
                runtime_source, legacy_status, partial_status
            ) VALUES (:document_id, :user_id, :source_pdf_path, :file_hash, :raw_markdown_path, :raw_json_path,
                :issuer_hint, :detected_issuer, :layout_family, :extraction_version, :page_count,
                :runtime_source, :legacy_status, :partial_status)
            """,
            asdict(document),
        )
        self.connection.commit()

    def get_document_by_hash(self, file_hash: str) -> RawDocument | None:
        row = self.connection.execute("SELECT * FROM documents WHERE file_hash = ?", (file_hash,)).fetchone()
        return RawDocument(**dict(row)) if row else None

    def save_statement(self, statement: InvoiceStatement) -> None:
        self.connection.execute(
            """
            INSERT OR REPLACE INTO statements (
                statement_id, document_id, user_id, issuer_name, card_fingerprint, billing_year, billing_month,
                statement_status, parse_confidence, card_label, card_last4, card_holder_name, statement_due_date,
                statement_close_date, statement_issue_date, statement_total_amount, minimum_payment_amount,
                credit_limit_amount, currency, runtime_source, legacy_status, partial_status
            ) VALUES (
                :statement_id, :document_id, :user_id, :issuer_name, :card_fingerprint, :billing_year, :billing_month,
                :statement_status, :parse_confidence, :card_label, :card_last4, :card_holder_name, :statement_due_date,
                :statement_close_date, :statement_issue_date, :statement_total_amount, :minimum_payment_amount,
                :credit_limit_amount, :currency, :runtime_source, :legacy_status, :partial_status
            )
            """,
            asdict(statement),
        )
        self.connection.commit()

    def list_statements(self, user_id: str) -> list[InvoiceStatement]:
        rows = self.connection.execute(
            """
            SELECT * FROM statements
            WHERE user_id = ? AND legacy_status != 'invalidated'
            ORDER BY billing_year DESC, billing_month DESC
            """,
            (user_id,),
        ).fetchall()
        return [InvoiceStatement(**dict(row)) for row in rows]

    def get_statement(self, statement_id: str) -> InvoiceStatement | None:
        row = self.connection.execute(
            "SELECT * FROM statements WHERE statement_id = ? AND legacy_status != 'invalidated'",
            (statement_id,),
        ).fetchone()
        return InvoiceStatement(**dict(row)) if row else None

    def list_statements_filtered(
        self,
        user_id: str,
        card_fingerprint: str | None = None,
        from_period: tuple[int, int] | None = None,
        to_period: tuple[int, int] | None = None,
    ) -> list[dict]:
        query = "SELECT * FROM statements WHERE user_id = ? AND legacy_status != 'invalidated'"
        params: list[object] = [user_id]
        if card_fingerprint:
            query += " AND card_fingerprint = ?"
            params.append(card_fingerprint)
        if from_period:
            query += " AND (billing_year * 100 + billing_month) >= ?"
            params.append(from_period[0] * 100 + from_period[1])
        if to_period:
            query += " AND (billing_year * 100 + billing_month) <= ?"
            params.append(to_period[0] * 100 + to_period[1])
        query += " ORDER BY billing_year DESC, billing_month DESC, statement_due_date DESC"
        rows = self.connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]

    def invalidate_legacy_history(self) -> None:
        self.connection.execute(
            """
            UPDATE documents
            SET legacy_status = 'invalidated'
            WHERE runtime_source != 'official'
            """
        )
        self.connection.execute(
            """
            UPDATE statements
            SET legacy_status = 'invalidated'
            WHERE runtime_source != 'official'
            """
        )
        self.connection.commit()
