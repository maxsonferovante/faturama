from __future__ import annotations

from faturama.infrastructure.opendataloader.extractor import extract_document


def test_extract_document_resolves_local_sidecars(invoice_dir):
    artifacts = extract_document(str(invoice_dir / "invoice-2026-04.pdf"))
    assert artifacts.output_dir.endswith("output/invoice-2026-04")
    assert artifacts.markdown_path.endswith("invoice-2026-04.md")
    assert artifacts.json_path.endswith("invoice-2026-04.json")
    assert artifacts.extraction_mode in {"generated", "reused"}
