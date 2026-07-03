"""Application read-side query service for PostgreSQL-backed read model."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
from decimal import Decimal
from typing import Any, Iterator
from urllib.parse import urlparse

from faturama.infrastructure.config.settings import Settings, load_settings
from faturama.infrastructure.database.postgres import connect_from_dsn
from faturama.infrastructure.repositories.installment_repository import InstallmentRepository
from faturama.infrastructure.repositories.review_repository import ReviewRepository
from faturama.infrastructure.repositories.statement_repository import StatementRepository
from faturama.infrastructure.repositories.summary_repository import SummaryRepository
from faturama.infrastructure.repositories.transaction_repository import TransactionRepository


class ReadModelQueryService:
    """Read-side service assembled at the application boundary for querying the database."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection
        self._statements = StatementRepository(connection)
        self._transactions = TransactionRepository(connection)
        self._summaries = SummaryRepository(connection)
        self._installments = InstallmentRepository(connection)
        self._reviews = ReviewRepository(connection)

    def close(self) -> None:
        self._connection.close()

    def query(self, name: str, **params: Any) -> Any:
        handlers = {
            "list_statements": self._list_statements,
            "show_statement": self._show_statement,
            "list_transactions": self._list_transactions,
            "monthly_spend": self._monthly_spend,
            "current_installments": self._current_installments,
            "future_installments": self._future_installments,
            "remaining_balance": self._remaining_balance,
            "list_review_items": self._list_review_items,
            "get_review_item": self._get_review_item,
            "resolve_review_item": self._resolve_review_item,
        }
        try:
            handler = handlers[name]
        except KeyError as exc:
            raise ValueError(f"Unknown query: {name}") from exc
        return handler(**params)

    def _list_statements(
        self,
        user_id: str,
        card_fingerprint: str | None = None,
        from_period: tuple[int, int] | None = None,
        to_period: tuple[int, int] | None = None,
    ) -> list[dict]:
        return self._statements.list_statements_filtered(user_id, card_fingerprint, from_period, to_period)

    def _show_statement(self, statement_id: str) -> dict | None:
        statement = self._statements.get_statement(statement_id)
        return asdict(statement) if statement else None

    def _list_transactions(
        self,
        statement_id: str,
        kind: str | None = None,
        installments_only: bool = False,
        review_status: str | None = None,
    ) -> list[dict]:
        return self._transactions.list_by_statement(statement_id, kind, installments_only, review_status)

    def _monthly_spend(
        self,
        user_id: str,
        year: int,
        month: int,
        card_fingerprint: str | None = None,
    ) -> list[dict]:
        rows = self._summaries.list_summaries(user_id, year, month)
        if card_fingerprint:
            rows = [row for row in rows if row["card_fingerprint"] == card_fingerprint]
        return rows

    def _current_installments(
        self,
        user_id: str,
        year: int,
        month: int,
        card_fingerprint: str | None = None,
    ) -> list[dict]:
        return self._transactions.list_by_month(
            user_id=user_id,
            year=year,
            month=month,
            kind="installment_charge",
            card_fingerprint=card_fingerprint,
        )

    def _future_installments(
        self,
        user_id: str,
        year: int,
        month: int,
        card_fingerprint: str | None = None,
    ) -> list[dict]:
        rows = self._installments.list_projections(year, month, user_id)
        if card_fingerprint:
            rows = [row for row in rows if row["card_fingerprint"] == card_fingerprint]
        return rows

    def _remaining_balance(
        self,
        user_id: str,
        card_fingerprint: str | None = None,
        plan_id: str | None = None,
    ) -> list[dict]:
        results: list[dict] = []
        for plan in self._installments.list_plans(user_id):
            if card_fingerprint and plan.card_fingerprint != card_fingerprint:
                continue
            if plan_id and plan.installment_plan_id != plan_id:
                continue
            rows = self._connection.execute(
                """
                SELECT * FROM projections
                WHERE installment_plan_id = %s
                ORDER BY projected_billing_year, projected_billing_month
                """,
                (plan.installment_plan_id,),
            ).fetchall()
            amount = Decimal("0")
            for row in rows:
                value = row["projected_amount"].replace("R$", "").replace(".", "").replace(",", ".").strip()
                amount += Decimal(value)
            results.append(
                {
                    "installment_plan_id": plan.installment_plan_id,
                    "card_fingerprint": plan.card_fingerprint,
                    "description_anchor": plan.description_anchor,
                    "installment_total": plan.installment_total,
                    "plan_status": plan.plan_status,
                    "remaining_balance": f"{amount:.2f}",
                }
            )
        return results

    def _list_review_items(
        self,
        user_id: str,
        entity_type: str | None = None,
        status: str | None = None,
        severity: str | None = None,
    ) -> list[dict]:
        return self._reviews.list_review_items_filtered(user_id, entity_type, status, severity)

    def _get_review_item(self, review_item_id: str) -> dict | None:
        return self._reviews.get_review_item(review_item_id)

    def _resolve_review_item(
        self,
        review_item_id: str,
        resolution_note: str,
        resolution_payload: dict | None = None,
    ) -> None:
        self._reviews.resolve_review_item(review_item_id, resolution_note, resolution_payload)


def require_database_dsn(settings: Settings | None = None) -> str:
    active_settings = settings or load_settings()
    dsn = active_settings.database_dsn
    if not dsn:
        raise RuntimeError("FATURAMA_DB_DSN is required for PostgreSQL-backed query services")

    parsed = urlparse(dsn)
    if parsed.scheme not in {"postgresql", "postgres"}:
        raise RuntimeError("FATURAMA_DB_DSN must use a PostgreSQL DSN")
    return dsn


@contextmanager
def read_model_query_service(settings: Settings | None = None) -> Iterator[ReadModelQueryService]:
    service = ReadModelQueryService(connect_from_dsn(require_database_dsn(settings)))
    try:
        yield service
    finally:
        service.close()
