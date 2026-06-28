"""Extraction service port."""

from __future__ import annotations

from typing import Protocol


class ExtractionService(Protocol):
    def extract(self, pdf_path: str, issuer_hint: str | None = None) -> tuple[str | None, str | None]: ...
