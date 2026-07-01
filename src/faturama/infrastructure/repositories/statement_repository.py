"""Statement repository implementation."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from faturama.domain.entities.invoice_statement import InvoiceStatement
from faturama.domain.entities.raw_document import RawDocument


def _upsert_clause(columns: Iterable[str], conflict_column: str) -> str:
    update_columns = [column for column in columns if column != conflict_column]
    assignments = ", ".join(f"{column} = EXCLUDED.{column}" for column in update_columns)
    return f"ON CONFLICT ({conflict_column}) DO UPDATE SET {assignments}"


class StatementRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def save_document(self, document: RawDocument) -> None:
        payload = asdict(document)
        columns = list(payload.keys())
        placeholders = ", ".join(["%s"] * len(columns))
        self.connection.execute(
            f"""
            INSERT INTO documents ({', '.join(columns)})
            VALUES ({placeholders})
            {_upsert_clause(columns, 'document_id')}
            """,
            tuple(payload[column] for column in columns),
        )

    def get_document_by_hash(self, file_hash: str) -> RawDocument | None:
        row = self.connection.execute("SELECT * FROM documents WHERE file_hash = %s", (file_hash,)).fetchone()
        return RawDocument(**dict(row)) if row else None

    def save_statement(self, statement: InvoiceStatement) -> None:
        payload = asdict(statement)
        columns = list(payload.keys())
        placeholders = ", ".join(["%s"] * len(columns))
        self.connection.execute(
            f"""
            INSERT INTO statements ({', '.join(columns)})
            VALUES ({placeholders})
            {_upsert_clause(columns, 'statement_id')}
            """,
            tuple(payload[column] for column in columns),
        )

    def list_statements(self, user_id: str) -> list[InvoiceStatement]:
        rows = self.connection.execute(
            """
            SELECT * FROM statements
            WHERE user_id = %s AND legacy_status != 'invalidated'
            ORDER BY billing_year DESC, billing_month DESC
            """,
            (user_id,),
        ).fetchall()
        return [InvoiceStatement(**dict(row)) for row in rows]

    def get_statement(self, statement_id: str) -> InvoiceStatement | None:
        row = self.connection.execute(
            "SELECT * FROM statements WHERE statement_id = %s AND legacy_status != 'invalidated'",
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
        query = "SELECT * FROM statements WHERE user_id = %s AND legacy_status != 'invalidated'"
        params: list[object] = [user_id]
        if card_fingerprint:
            query += " AND card_fingerprint = %s"
            params.append(card_fingerprint)
        if from_period:
            query += " AND (billing_year * 100 + billing_month) >= %s"
            params.append(from_period[0] * 100 + from_period[1])
        if to_period:
            query += " AND (billing_year * 100 + billing_month) <= %s"
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
