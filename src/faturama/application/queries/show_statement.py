"""Show statement query."""

from __future__ import annotations

from faturama.application.ports.query_service import QueryService


def execute(query_service: QueryService, statement_id: str) -> dict | None:
    return query_service.query("show_statement", statement_id=statement_id)
