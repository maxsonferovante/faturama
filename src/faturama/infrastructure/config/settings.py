"""Application settings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(slots=True)
class Settings:
    database_path: Path = Path("data/faturama.sqlite3")
    checkpoint_database_path: Path = Path("data/faturama-checkpoints.sqlite3")
    artifact_cache_dir: Path = Path("data/artifacts")
    confidence_threshold: float = 0.85
    agent_auto_apply_threshold: float = 0.97
    timezone: str = "America/Sao_Paulo"
    currency: str = "BRL"
    opendataloader_hybrid_url: str | None = None
    opendataloader_stub_mode: bool = False


def load_settings() -> Settings:
    return Settings(
        database_path=Path(os.getenv("FATURAMA_DB_PATH", "data/faturama.sqlite3")),
        checkpoint_database_path=Path(
            os.getenv("FATURAMA_CHECKPOINT_DB_PATH", "data/faturama-checkpoints.sqlite3")
        ),
        artifact_cache_dir=Path(os.getenv("FATURAMA_ARTIFACT_CACHE_DIR", "data/artifacts")),
        confidence_threshold=float(os.getenv("FATURAMA_CONFIDENCE_THRESHOLD", "0.85")),
        agent_auto_apply_threshold=float(os.getenv("FATURAMA_AGENT_AUTO_APPLY_THRESHOLD", "0.97")),
        timezone=os.getenv("FATURAMA_TIMEZONE", "America/Sao_Paulo"),
        currency=os.getenv("FATURAMA_CURRENCY", "BRL"),
        opendataloader_hybrid_url=os.getenv("FATURAMA_OPENDATALOADER_HYBRID_URL") or None,
        opendataloader_stub_mode=os.getenv("FATURAMA_OPENDATALOADER_STUB_MODE", "0") == "1",
    )
