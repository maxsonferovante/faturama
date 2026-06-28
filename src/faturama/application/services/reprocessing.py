"""Reprocessing helpers."""

from __future__ import annotations


def reconcile(existing: list[dict], incoming: list[dict], key: str) -> list[dict]:
    merged = {item[key]: item for item in existing}
    for item in incoming:
        merged[item[key]] = item
    return list(merged.values())
