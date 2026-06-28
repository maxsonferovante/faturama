"""DTOs for the async processing command contract."""

from __future__ import annotations

from typing import Any

from faturama.shared.pydantic_compat import BaseModel, ConfigDict, Field


class ProcessingCommandDTO(BaseModel):
    model_config = ConfigDict(extra="allow")

    processing_id: str
    bucket: str
    object_key: str
    event_time: str
    source: str
    upload_grant_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    artifact_prefix: str | None = None
    trace_id: str | None = None
    requested_by: str | None = None
