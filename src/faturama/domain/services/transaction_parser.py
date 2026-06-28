"""Rule-based transaction parser."""

from __future__ import annotations

import re

from faturama.domain.services.document_identity import line_hash


INSTALLMENT_RE = re.compile(r"parcela\s*(\d{1,2})\s*de\s*(\d{1,2})", re.IGNORECASE)


def normalize_description(description: str) -> str:
    normalized = re.sub(r"[^A-Z0-9 ]+", " ", description.upper())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def parse_candidate(statement_id: str, document_id: str, card_fingerprint: str, candidate: dict) -> dict:
    raw_text = candidate["raw_text"]
    description_raw = candidate["description_text"]
    amount = candidate["amount_text"].replace(" ", "")
    normalized = normalize_description(description_raw)
    merchant_normalized = INSTALLMENT_RE.sub("", normalized).strip()
    installment_match = INSTALLMENT_RE.search(description_raw)
    transaction_kind = "installment_charge" if installment_match else "new_purchase"
    current = int(installment_match.group(1)) if installment_match else None
    total = int(installment_match.group(2)) if installment_match else None
    confidence = 0.95 if installment_match else 0.9
    if not candidate.get("line_date_text"):
        confidence = min(confidence, 0.7)
    return {
        "statement_id": statement_id,
        "document_id": document_id,
        "card_fingerprint": card_fingerprint,
        "description_raw": description_raw,
        "description_normalized": normalized,
        "merchant_normalized": merchant_normalized or normalized,
        "amount": amount,
        "transaction_kind": transaction_kind,
        "line_hash": line_hash(statement_id, candidate["line_date_text"], normalized, amount, current, total),
        "parse_confidence": confidence,
        "posted_date": candidate["line_date_text"],
        "purchase_date": candidate["line_date_text"],
        "is_installment": bool(installment_match),
        "installment_current": current,
        "installment_total": total,
    }
