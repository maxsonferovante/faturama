"""OpenDataLoader adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from opendataloader_pdf import convert

from faturama.domain.exceptions import ArtifactNotFoundError
from faturama.infrastructure.files.artifacts import resolve_runtime_artifact_paths


@dataclass(slots=True)
class ExtractedArtifacts:
    markdown_path: str | None
    json_path: str | None
    output_dir: str | None = None
    extraction_mode: str = "generated"


def extract_artifacts(
    pdf_path: str,
    issuer_hint: str | None = None,
    artifact_root: str | Path | None = None,
    hybrid_url: str | None = None,
    stub_mode: bool = False,
) -> tuple[str | None, str | None, str | None, str]:
    del issuer_hint
    output_dir, md_path, json_path = resolve_runtime_artifact_paths(pdf_path, artifact_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    reused = md_path.exists() and json_path.exists()
    if stub_mode:
        _stub_convert(Path(pdf_path), output_dir, md_path, json_path)
    elif not reused:
        convert(
            pdf_path,
            output_dir=str(output_dir),
            format=["markdown", "json"],
            hybrid_url=hybrid_url,
            quiet=True,
        )
    if not md_path.exists() or not json_path.exists():
        raise ArtifactNotFoundError(f"Primary extraction did not produce artifacts for {pdf_path}")
    mode = "reused" if reused else "generated"
    return str(md_path), str(json_path), str(output_dir), mode


def extract_document(
    pdf_path: str,
    issuer_hint: str | None = None,
    artifact_root: str | Path | None = None,
    hybrid_url: str | None = None,
    stub_mode: bool = False,
) -> ExtractedArtifacts:
    markdown_path, json_path, output_dir, extraction_mode = extract_artifacts(
        pdf_path,
        issuer_hint,
        artifact_root=artifact_root,
        hybrid_url=hybrid_url,
        stub_mode=stub_mode,
    )
    return ExtractedArtifacts(
        markdown_path=markdown_path,
        json_path=json_path,
        output_dir=output_dir,
        extraction_mode=extraction_mode,
    )


def _stub_convert(pdf_path: Path, output_dir: Path, markdown_path: Path, json_path: Path) -> None:
    adjacent_markdown = pdf_path.with_suffix(".md")
    adjacent_json = pdf_path.with_suffix(".json")
    if adjacent_markdown.exists() and adjacent_json.exists():
        markdown_path.write_text(adjacent_markdown.read_text(encoding="utf-8"), encoding="utf-8")
        json_path.write_text(adjacent_json.read_text(encoding="utf-8"), encoding="utf-8")
        return
    raise ArtifactNotFoundError(f"Stub extraction requires adjacent fixture artifacts for {pdf_path}")
