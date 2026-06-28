"""Review context loading for ambiguous cases."""

from __future__ import annotations

import json
from pathlib import Path


def load_review_context(pdf_path: str, markdown_path: str | None, json_path: str | None) -> list[dict]:
    loader = _load_langchain_loader()
    if loader is not None:
        return loader(pdf_path)
    return _load_from_runtime_artifacts(markdown_path, json_path)


def _load_langchain_loader():
    try:
        from langchain_opendataloader_pdf import OpenDataLoaderPDFLoader  # type: ignore
    except Exception:
        return None

    def _loader(pdf_path: str) -> list[dict]:
        docs = OpenDataLoaderPDFLoader(
            file_path=pdf_path,
            format="markdown",
            quiet=True,
        ).load()
        return [
            {
                "page_content": doc.page_content,
                "metadata": dict(doc.metadata),
                "source": "langchain_opendataloader_pdf",
            }
            for doc in docs
        ]

    return _loader


def _load_from_runtime_artifacts(markdown_path: str | None, json_path: str | None) -> list[dict]:
    markdown = Path(markdown_path).read_text(encoding="utf-8") if markdown_path else ""
    metadata = {}
    if json_path and Path(json_path).exists():
        metadata = json.loads(Path(json_path).read_text(encoding="utf-8"))
    return [
        {
            "page_content": markdown,
            "metadata": metadata,
            "source": "runtime_artifacts",
        }
    ]
