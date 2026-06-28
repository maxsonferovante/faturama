from __future__ import annotations

from faturama.application.services.source_event_normalizer import build_dedupe_key
from faturama.application.services.reprocessing import should_ignore_source_delivery


def test_duplicate_events_share_same_dedupe_key():
    first = build_dedupe_key("bucket", "incoming/a.pdf", "2026-06-28T12:00:00Z", "etag", "v1")
    second = build_dedupe_key("bucket", "incoming/a.pdf", "2026-06-28T12:00:00Z", "etag", "v1")
    assert first == second
    assert should_ignore_source_delivery(existing_dedupe_key=first, incoming_dedupe_key=second)
