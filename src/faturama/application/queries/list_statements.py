"""List statement query."""

from __future__ import annotations

from faturama.application.ports.query_service import QueryService


def parse_period(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    year_str, month_str = value.split("-", 1)
    return int(year_str), int(month_str)


def execute(
    query_service: QueryService,
    user_id: str,
    card: str | None = None,
    from_: str | None = None,
    to: str | None = None,
) -> list[dict]:
    return query_service.query(
        "list_statements",
        user_id=user_id,
        card_fingerprint=card,
        from_period=parse_period(from_),
        to_period=parse_period(to),
    )
