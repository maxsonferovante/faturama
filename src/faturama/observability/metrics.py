"""In-memory metrics helpers."""

from __future__ import annotations

from collections import Counter


class MetricsRegistry:
    def __init__(self) -> None:
        self._counter: Counter[str] = Counter()

    def inc(self, key: str, amount: int = 1) -> None:
        self._counter[key] += amount

    def dump(self) -> dict[str, int]:
        return dict(self._counter)

    def snapshot(self, **extra: int) -> dict[str, int]:
        payload = self.dump()
        payload.update(extra)
        return payload

    def set(self, key: str, value: int) -> None:
        self._counter[key] = value
