"""Worker runtime that validates and executes async processing messages."""

from __future__ import annotations

from faturama.application.dto.processing_command_dto import ProcessingCommandDTO
from faturama.application.use_cases.process_processing_command import process_processing_command
from faturama.infrastructure.config.settings import Settings
from faturama.observability.logging import build_log_extra, get_logger


def run_processing_message(payload: dict[str, object], *, settings: Settings) -> dict[str, object]:
    logger = get_logger("faturama.async_worker")
    command = ProcessingCommandDTO.model_validate(payload)
    logger.info(
        "async_worker_started",
        extra=build_log_extra(
            event="async_worker_started",
            processing_id=command.processing_id,
            source_event_id=command.metadata.get("source_event_id"),
            eventbridge_id=command.metadata.get("eventbridge_id"),
            bucket=command.bucket,
            object_key=command.object_key,
            source=command.source,
        ),
    )
    result = process_processing_command(command, settings=settings)
    logger.info(
        "async_worker_completed",
        extra=build_log_extra(
            event="async_worker_completed",
            processing_id=command.processing_id,
            source_event_id=command.metadata.get("source_event_id"),
            eventbridge_id=command.metadata.get("eventbridge_id"),
            bucket=command.bucket,
            object_key=command.object_key,
            source=command.source,
            status=result["status"],
        ),
    )
    return result
