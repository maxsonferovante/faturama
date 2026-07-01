from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from faturama.infrastructure.config.settings import Settings
from tests.async_helpers import APRIL_MARKDOWN, write_async_source

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
def postgres_dsn(monkeypatch: pytest.MonkeyPatch) -> str:
    dsn = os.getenv("FATURAMA_TEST_DB_DSN") or os.getenv("FATURAMA_DB_DSN")
    if not dsn:
        pytest.skip("FATURAMA_TEST_DB_DSN or FATURAMA_DB_DSN is required for PostgreSQL integration tests")
    monkeypatch.setenv("FATURAMA_DB_DSN", dsn)
    return dsn


@pytest.fixture
def temp_db(postgres_dsn: str) -> str:
    return postgres_dsn


@pytest.fixture
def postgres_env(postgres_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    monkeypatch.setenv("FATURAMA_DB_DSN", postgres_dsn)
    monkeypatch.setenv("FATURAMA_ARTIFACT_CACHE_DIR", str(tmp_path / "output"))
    monkeypatch.setenv("FATURAMA_OPENDATALOADER_STUB_MODE", "1")
    monkeypatch.setenv("FATURAMA_AGENT_AUTO_APPLY_THRESHOLD", "0.92")
    return {
        "FATURAMA_DB_DSN": postgres_dsn,
        "FATURAMA_ARTIFACT_CACHE_DIR": str(tmp_path / "output"),
        "FATURAMA_OPENDATALOADER_STUB_MODE": "1",
        "FATURAMA_AGENT_AUTO_APPLY_THRESHOLD": "0.92",
        "PYTHONPATH": str(Path.cwd() / "src"),
    }


@pytest.fixture
def invoice_dir(tmp_path: Path) -> Path:
    write_invoice(tmp_path, "invoice-2026-04", APRIL_MARKDOWN)
    write_invoice(tmp_path, "invoice-2026-05", MAY_MARKDOWN)
    return tmp_path


@pytest.fixture
def cli_env(postgres_env: dict[str, str]) -> dict[str, str]:
    env = dict(os.environ)
    env.update(postgres_env)
    return env


@pytest.fixture
def async_storage_root(tmp_path: Path) -> Path:
    root = tmp_path / "object-store"
    root.mkdir(parents=True, exist_ok=True)
    return root

@pytest.fixture
def async_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, async_storage_root: Path) -> Settings:
    dsn = os.getenv("FATURAMA_TEST_DB_DSN") or os.getenv("FATURAMA_DB_DSN")
    if not dsn:
        pytest.skip("FATURAMA_TEST_DB_DSN or FATURAMA_DB_DSN is required for PostgreSQL integration tests")
    artifact_cache_dir = tmp_path / "artifacts"
    monkeypatch.setenv("FATURAMA_RUNTIME_ENV", "test")
    monkeypatch.setenv("FATURAMA_DB_DSN", dsn)
    monkeypatch.setenv("FATURAMA_ARTIFACT_CACHE_DIR", str(artifact_cache_dir))
    monkeypatch.setenv("FATURAMA_ARTIFACT_BUCKET", "processados-faturama")
    monkeypatch.setenv("FATURAMA_INPUT_BUCKET", "pre-processamento-faturama")
    monkeypatch.setenv("FATURAMA_ARTIFACT_PREFIX", "processed")
    monkeypatch.setenv("FATURAMA_OPENDATALOADER_STUB_MODE", "1")
    settings = Settings(
        runtime_env="test",
        aws_region="us-east-1",
        aws_endpoint_url="http://localhost:4566",
        input_bucket="pre-processamento-faturama",
        artifact_bucket="processados-faturama",
        artifact_prefix="processed",
        database_dsn=dsn,
        artifact_cache_dir=artifact_cache_dir,
        opendataloader_stub_mode=True,
    )
    (settings.artifact_cache_dir.parent / "object-store").mkdir(parents=True, exist_ok=True)
    return settings
