"""Document DTOs."""

from __future__ import annotations

from faturama.shared.pydantic_compat import BaseModel


class DocumentDTO(BaseModel):
    document_id: str
    user_id: str
    source_pdf_path: str
    file_hash: str
    raw_markdown_path: str | None = None
    raw_json_path: str | None = None
