"""DTOs for async status projection and artifacts."""

from __future__ import annotations

from faturama.shared.pydantic_compat import BaseModel


class ProcessingStatusDTO(BaseModel):
    processing_id: str
    document_id: str | None = None
    file_hash: str | None = None
    status: str
    is_terminal: bool
    review_required: bool
    status_detail: str | None = None
    result_reference: str | None = None
    artifact_manifest_id: str | None = None
    last_transition_at: str
    updated_at: str
