from __future__ import annotations

from faturama.infrastructure.opendataloader.issuer_layout_registry import detect_issuer


def test_detect_issuer_from_markdown():
    issuer, layout, confidence = detect_issuer("Fatura Inter cartao", None)
    assert issuer == "inter"
    assert layout == "inter-default"
    assert confidence > 0.0
