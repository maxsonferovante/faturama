"""Document repository port."""

from __future__ import annotations

from typing import Protocol

from faturama.domain.entities.raw_document import RawDocument


class DocumentRepository(Protocol):
    def save_document(self, document: RawDocument) -> None: ...
    def get_document_by_hash(self, file_hash: str) -> RawDocument | None: ...
