"""Reprocessing helpers."""

from __future__ import annotations

from collections.abc import Iterable

def reconcile(existing: list[dict], incoming: list[dict], key: str) -> list[dict]:
    merged = {item[key]: item for item in existing}
    for item in incoming:
        merged[item[key]] = item
    return list(merged.values())


def next_dispatch_attempt(previous_attempts: Iterable[int]) -> int:
    attempts = list(previous_attempts)
    return (max(attempts) if attempts else 0) + 1


def should_ignore_source_delivery(*, existing_dedupe_key: str | None, incoming_dedupe_key: str) -> bool:
    return existing_dedupe_key == incoming_dedupe_key
