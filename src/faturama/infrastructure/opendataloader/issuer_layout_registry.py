"""Issuer and layout registry."""

from __future__ import annotations

import re


def detect_issuer(markdown: str, issuer_hint: str | None = None) -> tuple[str, str, float]:
    if issuer_hint:
        return issuer_hint.lower(), f"{issuer_hint.lower()}-default", 1.0
    lowered = markdown.lower()
    for issuer in ("itau", "inter", "nubank", "bradesco", "santander"):
        if issuer in lowered:
            return issuer, f"{issuer}-default", 0.9
    return "unknown", "generic", 0.4


def extract_card_last4(markdown: str) -> str | None:
    match = re.search(r"(\d{4})\b", markdown)
    return match.group(1) if match else None
