"""Invoice ingestion use case."""

from __future__ import annotations

from pathlib import Path
import uuid

from faturama.application.services.workflow_builder import WorkflowBuilder
from faturama.application.services.workflow_state import WorkflowState
from faturama.application.services.workflow_nodes import (
    make_classify_transactions_node,
    make_extract_document_node,
    make_finalize_job_node,
    make_parse_statement_node,
    make_persist_canonical_data_node,
    make_resolve_ambiguities_node,
)
from faturama.domain.entities.invoice_statement import InvoiceStatement
from faturama.domain.entities.raw_document import RawDocument
from faturama.domain.services.document_identity import build_document_id, hash_file
from faturama.infrastructure.config.settings import Settings
from faturama.infrastructure.database.postgres import connect
from faturama.infrastructure.database.langgraph_checkpoint import LangGraphPostgresRuntime
from faturama.infrastructure.repositories.decision_repository import DecisionRepository
from faturama.infrastructure.repositories.evidence_repository import EvidenceRepository
from faturama.infrastructure.repositories.installment_repository import InstallmentRepository
from faturama.infrastructure.repositories.review_repository import ReviewRepository
from faturama.infrastructure.repositories.statement_repository import StatementRepository
from faturama.infrastructure.repositories.summary_repository import SummaryRepository
from faturama.infrastructure.repositories.transaction_repository import TransactionRepository
from faturama.observability.logging import get_logger
from faturama.observability.metrics import MetricsRegistry


def _build_card_fingerprint(card_last4: str | None, issuer_name: str | None) -> str:
    return f"{issuer_name or 'unknown'}:{card_last4 or '0000'}"


def _statement_id(document_id: str, card_fingerprint: str, billing_year: int, billing_month: int) -> str:
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"statement:{document_id}:{card_fingerprint}:{billing_year}-{billing_month:02d}",
        )
    )


def _transaction_id(statement_id: str, line_hash_value: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"transaction:{statement_id}:{line_hash_value}"))


def process_invoice(
    pdf_path: str,
    user_id: str,
    settings: Settings,
    issuer_hint: str | None = None,
    timezone: str | None = None,
    currency: str | None = None,
) -> dict:
    del timezone
    logger = get_logger("faturama.invoice_workflow")
    metrics = MetricsRegistry()
    db = connect(settings.database_dsn)
    statement_repo = StatementRepository(db)
    evidence_repo = EvidenceRepository(db)
    transaction_repo = TransactionRepository(db)
    installment_repo = InstallmentRepository(db)
    summary_repo = SummaryRepository(db)
    review_repo = ReviewRepository(db)
    decision_repo = DecisionRepository(db)
    langgraph_runtime = LangGraphPostgresRuntime(settings.database_dsn)
    checkpoint_store = langgraph_runtime.open()
    workflow = WorkflowBuilder()

    file_hash = hash_file(pdf_path)
    existing_document = statement_repo.get_document_by_hash(file_hash)
    document_id = existing_document.document_id if existing_document else build_document_id(file_hash)
    state = WorkflowState(pdf_path=pdf_path, user_id=user_id, issuer_hint=issuer_hint)
    initial_state = workflow.to_state_payload(state)
    initial_state["document_id"] = document_id
    initial_state["file_hash"] = file_hash
    initial_state["currency"] = currency or settings.currency
    logger.info(
        "invoice_workflow_started",
        extra={"event": "invoice_workflow_started", "job_id": state.job_id, "user_id": user_id, "pdf_path": pdf_path},
    )
    workflow.add_node("extract_document", make_extract_document_node(settings=settings, checkpoint_store=checkpoint_store))
    workflow.add_node("parse_statement", make_parse_statement_node(checkpoint_store=checkpoint_store))
    workflow.add_node("classify_transactions", make_classify_transactions_node(checkpoint_store=checkpoint_store))
    workflow.add_node(
        "resolve_ambiguities",
        make_resolve_ambiguities_node(
            settings=settings,
            checkpoint_store=checkpoint_store,
            statement_id_factory=_statement_id,
            transaction_id_factory=_transaction_id,
            evidence_repo=evidence_repo,
            review_repo=review_repo,
            decision_repo=decision_repo,
        ),
    )
    workflow.add_node(
        "persist_canonical_data",
        make_persist_canonical_data_node(
            settings=settings,
            checkpoint_store=checkpoint_store,
            statement_repo=statement_repo,
            transaction_repo=transaction_repo,
            installment_repo=installment_repo,
            summary_repo=summary_repo,
            raw_document_factory=RawDocument,
            invoice_statement_factory=InvoiceStatement,
        ),
    )
    workflow.add_node("finalize_job", make_finalize_job_node(checkpoint_store=checkpoint_store))
    workflow.add_default_flow()
    compiled = workflow.compile(checkpointer=checkpoint_store)
    try:
        result = compiled.invoke(
            initial_state,
            {"configurable": {"thread_id": state.thread_id, "checkpoint_ns": ""}},
        )
    except Exception:
        logger.exception(
            "invoice_workflow_failed",
            extra={"event": "invoice_workflow_failed", "job_id": state.job_id, "user_id": user_id, "pdf_path": pdf_path},
        )
        raise
    finally:
        langgraph_runtime.close()
        db.close()

    status = "review_required" if result["review_items"] else "parsed"
    metrics.inc("transactions_persisted", result.get("transactions_persisted", 0))
    metrics.inc("review_items_opened", len(result["review_items"]))
    payload = {
        "job_id": result["job_id"],
        "document_id": document_id,
        "file_hash": file_hash,
        "statement_ids": [result["statement_id"]],
        "status": status,
        "partial_status": "partial" if result["review_items"] else "complete",
        "transactions_persisted": result.get("transactions_persisted", 0),
        "installment_plans_updated": result.get("installment_plans_updated", 0),
        "projections_updated": result.get("projections_updated", 0),
        "review_items_opened": len(result["review_items"]),
        "source_pdf_path": str(Path(pdf_path)),
        "result_reference": f"document:{document_id}",
        "artifacts": {
            "markdown_path": str(result["artifacts"].get("markdown_path", "")),
            "json_path": str(result["artifacts"].get("json_path", "")),
            "output_dir": str(result["artifacts"].get("output_dir", "")),
        },
    }
    logger.info(
        "invoice_workflow_completed",
        extra={
            "event": "invoice_workflow_completed",
            "job_id": state.job_id,
            "user_id": user_id,
            "pdf_path": pdf_path,
            "status": status,
            "review_items_opened": payload["review_items_opened"],
            "transactions_persisted": payload["transactions_persisted"],
            "metrics": metrics.dump(),
        },
    )
    return payload

