"""Canonical workflow nodes for invoice processing."""

from __future__ import annotations

from dataclasses import asdict, fields
import json
from typing import Any

from faturama.application.services.ambiguity_resolution import resolve
from faturama.domain.entities.transaction_line import TransactionLine
from faturama.domain.services.confidence_policy import evaluate_transaction
from faturama.domain.services.future_projection import project_future_installments
from faturama.domain.services.header_extractor import extract_header
from faturama.domain.services.installment_matcher import build_plan
from faturama.domain.services.issuer_detector import detect_issuer
from faturama.domain.services.monthly_summary import build_summary
from faturama.domain.services.section_segmenter import segment
from faturama.domain.services.transaction_candidate_extractor import extract_candidates
from faturama.domain.services.transaction_parser import parse_candidate
from faturama.infrastructure.files.artifacts import require_artifacts
from faturama.infrastructure.llm.review_context_loader import load_review_context
from faturama.infrastructure.opendataloader.extractor import extract_document


_TRANSACTION_LINE_FIELDS = {field.name for field in fields(TransactionLine)}


def _to_transaction_line_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key in _TRANSACTION_LINE_FIELDS}


def _decode_resolution_payload(review_item: dict[str, Any] | None) -> dict[str, Any]:
    if not review_item:
        return {}
    payload = review_item.get("resolution_payload")
    if isinstance(payload, str) and payload:
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError:
            return {}
        return decoded if isinstance(decoded, dict) else {}
    return payload if isinstance(payload, dict) else {}


def make_extract_document_node(*, settings: Any, checkpoint_store: Any):
    def _node(state: dict) -> dict:
        artifact = extract_document(
            state["pdf_path"],
            state.get("issuer_hint"),
            artifact_root=settings.artifact_cache_dir,
            hybrid_url=settings.opendataloader_hybrid_url,
            stub_mode=settings.opendataloader_stub_mode,
        )
        markdown, raw_json = require_artifacts(
            markdown_path=artifact.markdown_path,
            json_path=artifact.json_path,
        )
        state["artifacts"] = {
            "markdown": markdown,
            "json": raw_json,
            "markdown_path": artifact.markdown_path,
            "json_path": artifact.json_path,
            "output_dir": artifact.output_dir,
            "extraction_mode": artifact.extraction_mode,
        }
        state["status"] = "extracting"
        checkpoint_id = checkpoint_store.save(
            state["job_id"], state["thread_id"], "extract_document", state, checkpoint_status="completed"
        )
        state["active_checkpoint_id"] = checkpoint_id
        return state

    return _node


def make_parse_statement_node(*, checkpoint_store: Any):
    def _node(state: dict) -> dict:
        markdown = state["artifacts"]["markdown"]
        issuer_name, layout_family, _ = detect_issuer(markdown, state.get("issuer_hint"))
        header = extract_header(markdown, issuer_name=issuer_name)
        state["header"] = header
        state["issuer_name"] = issuer_name
        state["layout_family"] = layout_family
        state["card_fingerprint"] = f"{issuer_name or 'unknown'}:{header.get('card_last4') or '0000'}"
        state["status"] = "parsing"
        checkpoint_id = checkpoint_store.save(
            state["job_id"], state["thread_id"], "parse_statement", state, checkpoint_status="completed"
        )
        state["active_checkpoint_id"] = checkpoint_id
        return state

    return _node


def make_classify_transactions_node(*, checkpoint_store: Any):
    def _node(state: dict) -> dict:
        sections = segment(state["artifacts"]["markdown"])
        candidates = extract_candidates(sections.get("transactions", sections.get("full", "")))
        state["candidates"] = candidates
        state["status"] = "classifying"
        checkpoint_id = checkpoint_store.save(
            state["job_id"], state["thread_id"], "classify_transactions", state, checkpoint_status="completed"
        )
        state["active_checkpoint_id"] = checkpoint_id
        return state

    return _node


def make_resolve_ambiguities_node(
    *,
    settings: Any,
    checkpoint_store: Any,
    statement_id_factory: Any,
    transaction_id_factory: Any,
    evidence_repo: Any,
    review_repo: Any,
    decision_repo: Any,
):
    def _node(state: dict) -> dict:
        header = state["header"]
        card_fingerprint = state["card_fingerprint"]
        statement_id = statement_id_factory(state["document_id"], card_fingerprint, header["billing_year"], header["billing_month"])
        context_documents = load_review_context(
            state["pdf_path"],
            state["artifacts"].get("markdown_path"),
            state["artifacts"].get("json_path"),
        )
        parsed_transactions: list[dict] = []
        review_items = []
        auto_applied_items = []
        for candidate in state.get("candidates", []):
            payload = parse_candidate(statement_id, state["document_id"], card_fingerprint, candidate)
            payload["transaction_id"] = transaction_id_factory(statement_id, payload["line_hash"])
            evidence_id = evidence_repo.save_evidence(
                document_id=state["document_id"],
                raw_text=candidate["raw_text"],
                page_number=candidate.get("page_number"),
                extraction_method="rule",
                structural_confidence=payload["parse_confidence"],
            )
            payload["source_evidence_id"] = evidence_id
            payload["raw_text"] = candidate["raw_text"]
            payload["page_number"] = candidate.get("page_number")
            payload = resolve(
                payload,
                confidence_threshold=settings.confidence_threshold,
                auto_apply_threshold=settings.agent_auto_apply_threshold,
                context_documents=context_documents,
            )
            review_status, decision_state, review_item, decision_payload = evaluate_transaction(
                user_id=state["user_id"],
                transaction=payload,
                threshold=settings.confidence_threshold,
            )
            resolved_review = review_repo.get_resolved_item_for_entity(payload["transaction_id"])
            if payload.get("agent_decision") == "auto_applied":
                review_status = "none"
                decision_state = "accepted_ai"
                review_item = None
                decision_payload["decision_state"] = "accepted_ai"
                decision_payload["decision_source"] = "ai_agent"
                decision_payload["decision_reason"] = payload.get("agent_reason", "Agent auto-applied decision")
                decision_payload["audit_payload"] = {
                    "agent_confidence": payload.get("agent_confidence"),
                    "auto_apply_threshold": settings.agent_auto_apply_threshold,
                    "source_strategy": payload.get("source_strategy"),
                }
                auto_applied_items.append(
                    {
                        "transaction_id": payload["transaction_id"],
                        "agent_confidence": payload.get("agent_confidence"),
                    }
                )
            elif review_item and resolved_review:
                resolution_payload = _decode_resolution_payload(resolved_review)
                review_status = "none"
                decision_state = "accepted_review"
                review_item = None
                payload["agent_decision"] = "human_resolved"
                decision_payload["decision_state"] = "accepted_review"
                decision_payload["decision_source"] = "human_review"
                decision_payload["decision_reason"] = resolved_review.get(
                    "resolution_note",
                    "Previously resolved review item reapplied during workflow resume",
                )
                decision_payload["audit_payload"] = {
                    "review_item_id": resolved_review.get("review_item_id"),
                    "resolution": resolution_payload.get("resolution"),
                    "note": resolution_payload.get("note"),
                    "resume_strategy": "resolved_review_reapplied",
                }
            payload["review_status"] = review_status
            payload["decision_state"] = decision_state
            parsed_transactions.append(payload)
            if review_item:
                review_repo.save_review_item(review_item)
                review_items.append(asdict(review_item))
            decision_repo.save_decision(decision_payload)
        state["statement_id"] = statement_id
        state["transactions"] = parsed_transactions
        state["review_items"] = review_items
        state["auto_applied_items"] = auto_applied_items
        state["status"] = "awaiting_review" if review_items else "persisting"
        checkpoint_id = checkpoint_store.save(
            state["job_id"],
            state["thread_id"],
            "resolve_ambiguities",
            state,
            checkpoint_status="active" if review_items else "completed",
            review_required=bool(review_items),
        )
        state["active_checkpoint_id"] = checkpoint_id
        return state

    return _node


def make_persist_canonical_data_node(
    *,
    settings: Any,
    checkpoint_store: Any,
    statement_repo: Any,
    transaction_repo: Any,
    installment_repo: Any,
    summary_repo: Any,
    raw_document_factory: Any,
    invoice_statement_factory: Any,
):
    def _future_balance(projections: list[dict]) -> str:
        total = 0.0
        for item in projections:
            normalized = item["projected_amount"].replace("R$", "").replace(".", "").replace(",", ".").strip()
            total += float(normalized)
        return f"{total:.2f}"

    def _node(state: dict) -> dict:
        header = state["header"]
        document = raw_document_factory(
            document_id=state["document_id"],
            user_id=state["user_id"],
            source_pdf_path=state["pdf_path"],
            file_hash=state["file_hash"],
            raw_markdown_path=state["artifacts"].get("markdown_path"),
            raw_json_path=state["artifacts"].get("json_path"),
            issuer_hint=state.get("issuer_hint"),
            detected_issuer=state.get("issuer_name"),
            layout_family=state.get("layout_family"),
            page_count=int(state["artifacts"]["json"].get("page_count", 1)),
            extraction_version="opendataloader-runtime",
            runtime_source="official",
            legacy_status="active",
            partial_status="partial" if state["review_items"] else "complete",
        )
        statement_repo.save_document(document)
        statement = invoice_statement_factory(
            statement_id=state["statement_id"],
            document_id=state["document_id"],
            user_id=state["user_id"],
            issuer_name=state.get("issuer_name"),
            card_fingerprint=state["card_fingerprint"],
            billing_year=header["billing_year"],
            billing_month=header["billing_month"],
            statement_status="partial" if state["review_items"] else "parsed",
            parse_confidence=0.95,
            card_last4=header.get("card_last4"),
            statement_due_date=header.get("statement_due_date"),
            statement_close_date=header.get("statement_close_date"),
            statement_issue_date=header.get("statement_issue_date"),
            statement_total_amount=header.get("statement_total_amount"),
            minimum_payment_amount=header.get("minimum_payment_amount"),
            credit_limit_amount=header.get("credit_limit_amount"),
            currency=settings.currency,
            runtime_source="official",
            legacy_status="active",
            partial_status="partial" if state["review_items"] else "complete",
        )
        statement_repo.save_statement(statement)
        plans_updated = 0
        projections_updated = 0
        for payload in state["transactions"]:
            transaction_repo.save_transaction(TransactionLine(**_to_transaction_line_payload(payload)))
            plan_payload = build_plan(user_id=state["user_id"], statement_id=state["statement_id"], transaction=payload)
            if not plan_payload:
                continue
            from faturama.domain.entities.installment_plan import InstallmentPlan
            from faturama.domain.entities.future_installment_projection import FutureInstallmentProjection

            installment_repo.save_plan(InstallmentPlan(**plan_payload))
            plans_updated += 1
            projected = project_future_installments(
                plan_payload,
                payload.get("installment_current"),
                statement.billing_year,
                statement.billing_month,
            )
            installment_repo.save_projections(
                plan_payload["installment_plan_id"],
                [FutureInstallmentProjection(**item) for item in projected],
            )
            projections_updated += len(projected)

        next_year = statement.billing_year + (1 if statement.billing_month == 12 else 0)
        next_month = 1 if statement.billing_month == 12 else statement.billing_month + 1
        future_projections = installment_repo.list_projections(next_year, next_month, state["user_id"])
        summary = build_summary(
            user_id=state["user_id"],
            statement=asdict(statement),
            transactions=state["transactions"],
            future_balance=_future_balance(future_projections),
        )
        summary["runtime_source"] = "official"
        summary["legacy_status"] = "active"
        summary_repo.upsert_summary(summary)
        state["transactions_persisted"] = len(state["transactions"])
        state["installment_plans_updated"] = plans_updated
        state["projections_updated"] = projections_updated
        state["statement"] = asdict(statement)
        state["status"] = "persisting"
        checkpoint_id = checkpoint_store.save(
            state["job_id"], state["thread_id"], "persist_canonical_data", state, checkpoint_status="completed"
        )
        state["active_checkpoint_id"] = checkpoint_id
        return state

    return _node


def make_finalize_job_node(*, checkpoint_store: Any):
    def _node(state: dict) -> dict:
        state["status"] = "review_required" if state["review_items"] else "completed"
        checkpoint_id = checkpoint_store.save(
            state["job_id"], state["thread_id"], "finalize_job", state, checkpoint_status="completed"
        )
        state["active_checkpoint_id"] = checkpoint_id
        return state

    return _node
