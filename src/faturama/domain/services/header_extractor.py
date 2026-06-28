"""Header extraction service."""

from __future__ import annotations

import re

from faturama.infrastructure.opendataloader.issuer_layout_registry import extract_card_last4


def _find_amount(markdown: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        match = re.search(rf"{label}.*?R\$\s*([0-9\.\,]+)", markdown, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
    return None


def _find_date(markdown: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        match = re.search(rf"{label}.*?(\d{{2}}/\d{{2}}/\d{{4}})", markdown, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
    return None


def extract_header(markdown: str, issuer_name: str | None = None) -> dict:
    card_last4 = extract_card_last4(markdown)
    due_date = _find_date(markdown, ("vencimento",))
    close_date = _find_date(markdown, ("fechamento",))
    issue_date = _find_date(markdown, ("emiss", "emissao"))
    total = _find_amount(markdown, ("total", "valor total"))
    minimum = _find_amount(markdown, ("pagamento minimo", "mínimo"))
    limit_amount = _find_amount(markdown, ("limite",))
    competence = issue_date or due_date or "01/01/1970"
    day, month, year = competence.split("/")
    del day
    return {
        "issuer_name": issuer_name,
        "card_last4": card_last4,
        "billing_year": int(year),
        "billing_month": int(month),
        "statement_due_date": due_date,
        "statement_close_date": close_date,
        "statement_issue_date": issue_date,
        "statement_total_amount": total,
        "minimum_payment_amount": minimum,
        "credit_limit_amount": limit_amount,
    }
