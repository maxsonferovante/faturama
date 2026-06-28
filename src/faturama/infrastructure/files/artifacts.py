"""Artifact loading helpers."""

from __future__ import annotations

import json
from pathlib import Path

from faturama.domain.exceptions import ArtifactNotFoundError


def resolve_runtime_artifact_paths(pdf_path: str, artifact_root: str | Path | None = None) -> tuple[Path, Path, Path]:
    pdf = Path(pdf_path)
    output_dir = Path(artifact_root) / pdf.stem if artifact_root else pdf.parent / "output" / pdf.stem
    return output_dir, output_dir / f"{pdf.stem}.md", output_dir / f"{pdf.stem}.json"


def load_markdown(markdown_path: str | Path | None) -> str:
    if markdown_path is None:
        return ""
    return Path(markdown_path).read_text(encoding="utf-8")


def load_json(json_path: str | Path | None) -> dict:
    if json_path is None:
        return {}
    return json.loads(Path(json_path).read_text(encoding="utf-8"))


def require_artifacts(pdf_path: str | None = None, markdown_path: str | Path | None = None, json_path: str | Path | None = None) -> tuple[str, dict]:
    if markdown_path is not None or json_path is not None:
        md_path = Path(markdown_path) if markdown_path is not None else None
        json_file = Path(json_path) if json_path is not None else None
    else:
        raise ArtifactNotFoundError("No artifact coordinates were provided")
    if md_path is None or json_file is None:
        target = pdf_path or str(markdown_path or json_path)
        raise ArtifactNotFoundError(f"Could not locate extracted artifacts for {target}")
    return load_markdown(md_path), load_json(json_file)
