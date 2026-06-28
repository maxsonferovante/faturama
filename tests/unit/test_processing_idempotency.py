from __future__ import annotations

from faturama.application.services.source_event_normalizer import build_dedupe_key
from faturama.application.services.reprocessing import should_ignore_source_delivery


def test_dedupe_key_is_stable_for_same_event():
    first = build_dedupe_key("bucket", "invoice.pdf", "2026-06-28T12:00:00Z", "etag", "v1")
    second = build_dedupe_key("bucket", "invoice.pdf", "2026-06-28T12:00:00Z", "etag", "v1")
    assert first == second


def test_duplicate_source_delivery_can_be_ignored():
    assert should_ignore_source_delivery(existing_dedupe_key="same", incoming_dedupe_key="same")
