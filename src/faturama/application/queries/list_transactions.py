"""List statement transactions query."""

from __future__ import annotations

from faturama.application.ports.query_service import QueryService


def execute(
    query_service: QueryService,
    statement_id: str,
    kind: str | None = None,
    installments_only: bool = False,
    review_status: str | None = None,
) -> list[dict]:
    return query_service.query(
        "list_transactions",
        statement_id=statement_id,
        kind=kind,
        installments_only=installments_only,
        review_status=review_status,
    )
