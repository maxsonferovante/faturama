from __future__ import annotations

from faturama.application.services.reprocessing import reconcile


def test_reconcile_replaces_existing_item_by_key():
    merged = reconcile([{"line_hash": "a", "amount": "1"}], [{"line_hash": "a", "amount": "2"}], "line_hash")
    assert merged == [{"line_hash": "a", "amount": "2"}]
