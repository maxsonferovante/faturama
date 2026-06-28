from __future__ import annotations

from faturama.application.queries.list_statements import parse_period


def test_parse_period_returns_year_and_month():
    assert parse_period("2026-04") == (2026, 4)
