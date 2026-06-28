"""Confidence policy service."""

from __future__ import annotations

import uuid

from faturama.domain.entities.review_item import ReviewItem


def evaluate_transaction(user_id: str, transaction: dict, threshold: float) -> tuple[str, str, ReviewItem | None, dict]:
    confidence = float(transaction["parse_confidence"])
    if confidence < threshold:
        review_item = ReviewItem(
            review_item_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"review:{transaction['transaction_id']}")),
            user_id=user_id,
            entity_type="transaction",
            entity_id=transaction["transaction_id"],
            reason_code="low_confidence",
            reason_detail=f"Transaction confidence {confidence:.2f} below threshold {threshold:.2f}",
            confidence_threshold_snapshot=threshold,
            severity="medium",
            status="open",
        )
        decision_state = "review_required"
        review_status = "open"
    else:
        review_item = None
        decision_state = "accepted_high" if confidence >= 0.95 else "accepted_medium"
        review_status = "none"
    decision_payload = {
        "decision_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"decision:{transaction['transaction_id']}")),
        "entity_type": "transaction",
        "entity_id": transaction["transaction_id"],
        "decision_state": decision_state,
        "confidence_structural": confidence,
        "confidence_semantic": confidence,
        "confidence_relational": confidence if transaction.get("is_installment") else 1.0,
        "confidence_operational": confidence,
        "decision_reason": "Automatic confidence policy evaluation",
    }
    return review_status, decision_state, review_item, decision_payload
