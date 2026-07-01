"""Remaining balance query."""

from __future__ import annotations

from faturama.application.ports.query_service import QueryService


def execute(query_service: QueryService, user_id: str, card: str | None = None, plan_id: str | None = None) -> list[dict]:
    return query_service.query(
        "remaining_balance",
        user_id=user_id,
        card_fingerprint=card,
        plan_id=plan_id,
    )
