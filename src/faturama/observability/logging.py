"""Logging helpers."""

from __future__ import annotations

import json
import logging


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in (
            "event",
            "processing_id",
            "source_event_id",
            "eventbridge_id",
            "report_id",
            "repository_root",
            "metrics",
            "markdown_output_path",
            "error_code",
            "bucket",
            "object_key",
            "source",
            "job_id",
            "user_id",
            "pdf_path",
            "status",
            "status_detail",
            "artifact_manifest_id",
            "review_items_opened",
            "transactions_persisted",
        ):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str = "faturama") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def build_log_extra(**extra: object) -> dict[str, object]:
    return {key: value for key, value in extra.items() if value is not None}
