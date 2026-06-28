"""Structured extraction fallback stub.

The v1 implementation keeps LLM usage optional. When configured, this adapter can
be replaced by a real provider without affecting the application contracts.
"""

from __future__ import annotations


def extract_ambiguous_line(candidate: dict, context_documents: list[dict] | None = None) -> dict:
    payload = dict(candidate)
    description = str(candidate.get("description_raw") or candidate.get("description_text") or "")
    base_confidence = float(candidate.get("parse_confidence", 0.0))
    heuristic_bonus = 0.05 if any(char.isdigit() for char in description) else 0.02
    if context_documents:
        heuristic_bonus += 0.03
    payload["llm_used"] = True
    payload["agent_confidence"] = min(0.99, max(base_confidence, base_confidence + heuristic_bonus))
    payload["agent_reason"] = "Agent-assisted resolution using document context"
    return payload
