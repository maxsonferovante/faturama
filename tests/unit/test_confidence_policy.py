from __future__ import annotations

from faturama.domain.services.confidence_policy import evaluate_transaction


def test_low_confidence_transaction_opens_review():
    review_status, decision_state, review_item, decision = evaluate_transaction(
        "demo",
        {"transaction_id": "tx-1", "parse_confidence": 0.7, "is_installment": False},
        0.85,
    )
    assert review_status == "open"
    assert decision_state == "review_required"
    assert review_item is not None
    assert decision["entity_id"] == "tx-1"
