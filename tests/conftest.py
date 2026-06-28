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


def _write_usage_report_repo(base_dir: Path) -> Path:
    (base_dir / "src/faturama/application/use_cases").mkdir(parents=True, exist_ok=True)
    (base_dir / "src/faturama/application/services").mkdir(parents=True, exist_ok=True)
    (base_dir / "src/faturama/infrastructure/files").mkdir(parents=True, exist_ok=True)
    (base_dir / "src/faturama/infrastructure/opendataloader").mkdir(parents=True, exist_ok=True)
    (base_dir / "specs/001-invoice-extractor").mkdir(parents=True, exist_ok=True)

    (base_dir / "pyproject.toml").write_text(
        """
[project]
name = "usage-report-fixture"
dependencies = [
  "langgraph>=0.2,<1",
  "opendataloader-pdf[hybrid]>=0.1",
]
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (base_dir / "README.md").write_text(
        "\n".join(
            [
                "# Fixture",
                "LangGraph usado em runtime para coordenar o workflow principal.",
                "OpenDataLoader usado em runtime como extrator primário do PDF.",
                "Workflow orientado a checkpoints.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base_dir / "specs/001-invoice-extractor/plan.md").write_text(
        "\n".join(
            [
                "Primary Dependencies: opendataloader-pdf[hybrid], langgraph",
                "LangGraph para orquestração com checkpoints.",
                "OpenDataLoader como extração base.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base_dir / "specs/001-invoice-extractor/spec.md").write_text(
        "\n".join(
            [
                "LangGraph deve controlar o estado do workflow.",
                "OpenDataLoader deve ser o extrator primário.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base_dir / "src/faturama/application/use_cases/process_invoice.py").write_text(
        "\n".join(
            [
                "from faturama.application.services.workflow_builder import WorkflowBuilder",
                "from faturama.infrastructure.files.artifacts import require_artifacts",
                "from faturama.infrastructure.opendataloader.extractor import extract_document",
                "workflow = WorkflowBuilder()",
                "workflow.checkpoint(None, 'ingest_document')",
                "workflow.save_checkpoint(None, 'checkpoints')",
                "extract_document('invoice.pdf')",
                "require_artifacts(pdf_path='invoice.pdf')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base_dir / "src/faturama/application/services/workflow_builder.py").write_text(
        "\n".join(
            [
                "class WorkflowBuilder:",
                "    def checkpoint(self, state, name):",
                "        return state",
                "    def save_checkpoint(self, state, directory):",
                "        return directory",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base_dir / "src/faturama/infrastructure/files/artifacts.py").write_text(
        "\n".join(
            [
                "def resolve_sidecar_paths(pdf_path):",
                "    return pdf_path.replace('.pdf', '.md'), pdf_path.replace('.pdf', '.json')",
                "def require_artifacts(pdf_path):",
                "    return resolve_sidecar_paths(pdf_path)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base_dir / "src/faturama/infrastructure/opendataloader/extractor.py").write_text(
        "\n".join(
            [
                '"""Adapter only."""',
                "from faturama.infrastructure.files.artifacts import resolve_sidecar_paths",
                "def extract_document(pdf_path):",
                "    return resolve_sidecar_paths(pdf_path)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return base_dir


@pytest.fixture
def usage_report_repo(tmp_path: Path) -> Path:
    return _write_usage_report_repo(tmp_path / "usage-report-repo")


@pytest.fixture
def usage_cli_env(cli_env: dict[str, str], usage_report_repo: Path) -> dict[str, str]:
    env = dict(cli_env)
    env["FATURAMA_USAGE_REPORT_ROOT"] = str(usage_report_repo)
    return env
