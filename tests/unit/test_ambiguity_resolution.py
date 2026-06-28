from __future__ import annotations

from faturama.application.services.ambiguity_resolution import resolve


def test_resolve_skips_agent_when_confidence_is_already_high():
    payload = resolve(
        {
            "transaction_id": "tx-1",
            "description_raw": "SUPERMERCADO CENTRAL",
            "parse_confidence": 0.96,
        },
        confidence_threshold=0.9,
        auto_apply_threshold=0.97,
        context_documents=[],
    )

    assert payload["agent_decision"] == "not_needed"
    assert payload["source_strategy"] == "rule"


def test_resolve_auto_applies_when_agent_confidence_reaches_high_threshold():
    payload = resolve(
        {
            "transaction_id": "tx-2",
            "description_raw": "COMPRA 1234",
            "parse_confidence": 0.9,
        },
        confidence_threshold=0.95,
        auto_apply_threshold=0.97,
        context_documents=[{"page_content": "contexto"}],
    )

    assert payload["llm_used"] is True
    assert payload["agent_decision"] == "auto_applied"
    assert payload["review_status"] == "none"
    assert payload["decision_state"] == "accepted_ai"


def test_resolve_routes_to_human_review_when_agent_confidence_is_not_enough():
    payload = resolve(
        {
            "transaction_id": "tx-3",
            "description_raw": "ASSINATURA DIGITAL",
            "parse_confidence": 0.9,
        },
        confidence_threshold=0.95,
        auto_apply_threshold=0.99,
        context_documents=[],
    )

    assert payload["llm_used"] is True
    assert payload["agent_decision"] == "human_required"
    assert payload["review_status"] == "open"
