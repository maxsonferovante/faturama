from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


APRIL_MARKDOWN = """Inter Cartao final 1234
Emissao 10/04/2026
Fechamento 15/04/2026
Vencimento 20/04/2026
Valor total R$ 672,89
Pagamento minimo R$ 100,00
Limite R$ 5.000,00

Compras
14/04/2026 MERCADOLIVRE (Parcela 02 de 10) R$ 422,89
15/04/2026 SUPERMERCADO CENTRAL R$ 200,00
ASSINATURA DIGITAL R$ 50,00
"""

MAY_MARKDOWN = """Inter Cartao final 1234
Emissao 10/05/2026
Fechamento 15/05/2026
Vencimento 20/05/2026
Valor total R$ 722,89
Pagamento minimo R$ 100,00
Limite R$ 5.000,00

Compras
14/05/2026 MERCADOLIVRE (Parcela 03 de 10) R$ 422,89
16/05/2026 FARMACIA VIDA R$ 300,00
"""


def write_invoice(base_dir: Path, stem: str, markdown: str) -> Path:
    pdf_path = base_dir / f"{stem}.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake invoice")
    pdf_path.with_suffix(".md").write_text(markdown, encoding="utf-8")
    pdf_path.with_suffix(".json").write_text(json.dumps({"page_count": 1}), encoding="utf-8")
    output_dir = base_dir / "output" / stem
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{stem}.md").write_text(markdown, encoding="utf-8")
    (output_dir / f"{stem}.json").write_text(json.dumps({"page_count": 1}), encoding="utf-8")
    return pdf_path


@pytest.fixture
def temp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "faturama.sqlite3"
    monkeypatch.setenv("FATURAMA_DB_PATH", str(db_path))
    monkeypatch.setenv("FATURAMA_CHECKPOINT_DB_PATH", str(tmp_path / "faturama-checkpoints.sqlite3"))
    monkeypatch.setenv("FATURAMA_ARTIFACT_CACHE_DIR", str(tmp_path / "output"))
    monkeypatch.setenv("FATURAMA_OPENDATALOADER_STUB_MODE", "1")
    monkeypatch.setenv("FATURAMA_AGENT_AUTO_APPLY_THRESHOLD", "0.92")
    return db_path


@pytest.fixture
def invoice_dir(tmp_path: Path) -> Path:
    write_invoice(tmp_path, "invoice-2026-04", APRIL_MARKDOWN)
    write_invoice(tmp_path, "invoice-2026-05", MAY_MARKDOWN)
    return tmp_path


@pytest.fixture
def cli_env(temp_db: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["FATURAMA_DB_PATH"] = str(temp_db)
    env["FATURAMA_CHECKPOINT_DB_PATH"] = str(temp_db.with_name("faturama-checkpoints.sqlite3"))
    env["FATURAMA_ARTIFACT_CACHE_DIR"] = str(temp_db.parent / "output")
    env["FATURAMA_OPENDATALOADER_STUB_MODE"] = "1"
    env["FATURAMA_AGENT_AUTO_APPLY_THRESHOLD"] = "0.92"
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    return env
