from __future__ import annotations

from faturama.application.services.source_event_normalizer import build_dedupe_key


def test_out_of_order_event_delivery_produces_distinct_dedupe_key():
    earlier = build_dedupe_key("bucket", "incoming/a.pdf", "2026-06-28T12:00:00Z", "etag", "v1")
    later = build_dedupe_key("bucket", "incoming/a.pdf", "2026-06-28T12:00:05Z", "etag", "v1")
    assert earlier != later
