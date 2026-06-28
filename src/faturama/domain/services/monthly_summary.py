"""Monthly summary calculations."""

from __future__ import annotations

from decimal import Decimal
import uuid


def _sum_amounts(transactions: list[dict], kinds: set[str]) -> str:
    total = Decimal("0")
    for transaction in transactions:
        if transaction["transaction_kind"] in kinds:
            amount = transaction["amount"].replace("R$", "").replace(".", "").replace(",", ".")
            total += Decimal(amount)
    return f"{total:.2f}"


def build_summary(user_id: str, statement: dict, transactions: list[dict], future_balance: str) -> dict:
    return {
        "summary_id": str(uuid.uuid4()),
        "user_id": user_id,
        "card_fingerprint": statement["card_fingerprint"],
        "issuer_name": statement.get("issuer_name"),
        "card_label": statement.get("card_label"),
        "billing_year": statement["billing_year"],
        "billing_month": statement["billing_month"],
        "statement_total_amount": statement.get("statement_total_amount"),
        "new_purchase_total": _sum_amounts(transactions, {"new_purchase"}),
        "installment_charge_total": _sum_amounts(transactions, {"installment_charge"}),
        "invoice_financing_total": _sum_amounts(transactions, {"invoice_installment"}),
        "interest_and_fees_total": _sum_amounts(transactions, {"interest_fee", "tax_fee"}),
        "refund_total": _sum_amounts(transactions, {"refund"}),
        "future_installment_balance": future_balance,
        "next_cycle_installment_commitment": future_balance,
    }
