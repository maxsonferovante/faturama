"""Issuer detector service."""

from __future__ import annotations

from faturama.infrastructure.opendataloader.issuer_layout_registry import detect_issuer as detect_registry_issuer


def detect(markdown: str, issuer_hint: str | None = None) -> tuple[str, str]:
    issuer_name, layout_family, confidence = detect_registry_issuer(markdown, issuer_hint)
    del confidence
    return issuer_name, layout_family


def detect_issuer(markdown: str, issuer_hint: str | None = None) -> tuple[str, str, float]:
    issuer_name, layout_family = detect(markdown, issuer_hint)
    return issuer_name, layout_family, 1.0 if issuer_hint else 0.9
