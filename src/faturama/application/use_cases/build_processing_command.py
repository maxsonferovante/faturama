"""Build canonical processing commands from source events."""

from __future__ import annotations

from typing import Any

from faturama.application.dto.processing_command_dto import ProcessingCommandDTO
from faturama.application.services.source_event_normalizer import normalize_source_event


def build_processing_command(payload: dict[str, Any], *, artifact_prefix: str) -> tuple[dict[str, Any], ProcessingCommandDTO]:
    normalized = normalize_source_event(payload, artifact_prefix=artifact_prefix)
    command = ProcessingCommandDTO.model_validate(normalized["processing_command"])
    return normalized, command
