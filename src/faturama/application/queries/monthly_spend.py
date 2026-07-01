"""Monthly spend query."""

from __future__ import annotations

from faturama.application.ports.query_service import QueryService


def execute(query_service: QueryService, user_id: str, month: str, card: str | None = None) -> list[dict]:
    year_str, month_str = month.split("-", 1)
    return query_service.query(
        "monthly_spend",
        user_id=user_id,
        year=int(year_str),
        month=int(month_str),
        card_fingerprint=card,
    )
