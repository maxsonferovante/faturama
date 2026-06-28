"""Installment matching service."""

from __future__ import annotations

import uuid


def canonical_key(
    merchant_normalized: str,
    amount: str,
    card_fingerprint: str,
    installment_total: int | None,
) -> str:
    total_part = installment_total if installment_total is not None else "unknown-total"
    return f"{merchant_normalized}|{amount}|{card_fingerprint}|{total_part}"


def build_plan(user_id: str, statement_id: str, transaction: dict) -> dict | None:
    if not transaction.get("is_installment"):
        return None
    key = canonical_key(
        transaction["merchant_normalized"],
        transaction["amount"],
        transaction["card_fingerprint"],
        transaction.get("installment_total"),
    )
    return {
        "installment_plan_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"installment-plan:{key}")),
        "user_id": user_id,
        "card_fingerprint": transaction["card_fingerprint"],
        "installment_type": transaction["transaction_kind"],
        "description_anchor": transaction["description_raw"],
        "description_normalized": transaction["description_normalized"],
        "merchant_normalized": transaction["merchant_normalized"],
        "origin_purchase_date": transaction.get("purchase_date"),
        "installment_amount": transaction["amount"],
        "installment_total": transaction["installment_total"],
        "first_seen_statement_id": statement_id,
        "last_seen_statement_id": statement_id,
        "plan_status": "active",
        "plan_confidence": transaction["parse_confidence"],
        "matching_strategy": "canonical-key",
        "canonical_key": key,
    }
