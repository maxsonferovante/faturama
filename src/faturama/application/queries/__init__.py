"""Query entrypoints."""

from faturama.application.queries import (
    current_installments,
    future_installments,
    list_statements,
    list_transactions,
    monthly_spend,
    remaining_balance,
    show_statement,
)

__all__ = [
    "current_installments",
    "future_installments",
    "list_statements",
    "list_transactions",
    "monthly_spend",
    "remaining_balance",
    "show_statement",
]
