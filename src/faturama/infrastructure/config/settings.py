"""Application settings."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import os

from faturama.infrastructure.database.postgres import DatabaseConfigurationError, validate_postgres_dsn


@dataclass(slots=True)
class Settings:
    runtime_env: str = "local"
    aws_region: str = "us-east-1"
    aws_endpoint_url: str | None = None
    input_bucket: str = "pre-processamento-faturama"
    artifact_bucket: str = "processados-faturama"
    artifact_prefix: str = "processed"
    processing_message: str | None = None
    database_dsn: str = ""
    log_level: str = "INFO"
    signed_upload_expiration_seconds: int = 300
    artifact_cache_dir: Path = Path("data/artifacts")
    confidence_threshold: float = 0.85
    agent_auto_apply_threshold: float = 0.97
    timezone: str = "America/Sao_Paulo"
    currency: str = "BRL"
    opendataloader_hybrid_url: str | None = None
    opendataloader_stub_mode: bool = False

    def __post_init__(self) -> None:
        self.database_dsn = validate_postgres_dsn(self.database_dsn)

    def processing_message_payload(self) -> dict[str, object]:
        if not self.processing_message:
            return {}
        try:
            payload = json.loads(self.processing_message)
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}


def load_settings() -> Settings:
    database_dsn = os.getenv("FATURAMA_DB_DSN")
    if not database_dsn:
        raise DatabaseConfigurationError("FATURAMA_DB_DSN is required")

    return Settings(
        runtime_env=os.getenv("FATURAMA_RUNTIME_ENV", "local"),
        aws_region=os.getenv("FATURAMA_AWS_REGION", "us-east-1"),
        aws_endpoint_url=os.getenv("FATURAMA_AWS_ENDPOINT_URL") or None,
        input_bucket=os.getenv("FATURAMA_INPUT_BUCKET", "pre-processamento-faturama"),
        artifact_bucket=os.getenv("FATURAMA_ARTIFACT_BUCKET", "processados-faturama"),
        artifact_prefix=os.getenv("FATURAMA_ARTIFACT_PREFIX", "processed"),
        processing_message=os.getenv("FATURAMA_PROCESSING_MESSAGE") or None,
        database_dsn=database_dsn,
        log_level=os.getenv("FATURAMA_LOG_LEVEL", "INFO"),
        signed_upload_expiration_seconds=int(os.getenv("FATURAMA_SIGNED_UPLOAD_EXPIRATION_SECONDS", "300")),
        artifact_cache_dir=Path(os.getenv("FATURAMA_ARTIFACT_CACHE_DIR", "data/artifacts")),
        confidence_threshold=float(os.getenv("FATURAMA_CONFIDENCE_THRESHOLD", "0.85")),
        agent_auto_apply_threshold=float(os.getenv("FATURAMA_AGENT_AUTO_APPLY_THRESHOLD", "0.97")),
        timezone=os.getenv("FATURAMA_TIMEZONE", "America/Sao_Paulo"),
        currency=os.getenv("FATURAMA_CURRENCY", "BRL"),
        opendataloader_hybrid_url=os.getenv("FATURAMA_OPENDATALOADER_HYBRID_URL") or None,
        opendataloader_stub_mode=os.getenv("FATURAMA_OPENDATALOADER_STUB_MODE", "0") == "1",
    )
