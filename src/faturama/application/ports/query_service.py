"""Query service port."""

from __future__ import annotations

from typing import Any, Protocol


class QueryService(Protocol):
    def query(self, name: str, **params: Any) -> Any: ...
