"""Validated ambiguity resolution service."""

from __future__ import annotations

from faturama.infrastructure.llm.structured_extractor import extract_ambiguous_line


def resolve(
    transaction: dict,
    *,
    confidence_threshold: float,
    auto_apply_threshold: float,
    context_documents: list[dict] | None = None,
) -> dict:
    payload = dict(transaction)
    parse_confidence = float(payload["parse_confidence"])
    payload["source_strategy"] = payload.get("source_strategy", "rule")
    payload["agent_decision"] = "not_needed"
    if parse_confidence >= confidence_threshold:
        return payload

    enriched = extract_ambiguous_line(payload, context_documents=context_documents)
    payload.update(enriched)
    payload["source_strategy"] = "ai_agent"
    agent_confidence = float(payload.get("agent_confidence", 0.0))
    if agent_confidence >= auto_apply_threshold:
        payload["agent_decision"] = "auto_applied"
        payload["decision_state"] = "accepted_ai"
        payload["review_status"] = "none"
    else:
        payload["agent_decision"] = "human_required"
        payload["review_status"] = "open"
    return payload
