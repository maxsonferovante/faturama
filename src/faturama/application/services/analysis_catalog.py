"""Catalog of targets analyzed by the usage report."""

from __future__ import annotations

from faturama.domain.entities.analysis_target import AnalysisTarget


def build_analysis_catalog() -> list[AnalysisTarget]:
    return [
        AnalysisTarget(
            target_id="langgraph-runtime",
            target_name="LangGraph",
            target_kind="library",
            scope_group="workflow",
            expected_behavior="LangGraph deve orquestrar o workflow principal de ingestão com checkpoints reais de runtime.",
            expected_markers=("langgraph", "StateGraph", "compile("),
        ),
        AnalysisTarget(
            target_id="opendataloader-runtime",
            target_name="OpenDataLoader",
            target_kind="library",
            scope_group="extraction",
            expected_behavior="OpenDataLoader deve executar a extração primária do PDF, não apenas naming ou sidecars pré-gerados.",
            expected_markers=("opendataloader", "opendataloader_pdf", "convert("),
        ),
        AnalysisTarget(
            target_id="workflow-checkpoints",
            target_name="Workflow Checkpoints",
            target_kind="pipeline_signal",
            scope_group="workflow",
            expected_behavior="O pipeline atual deve expor um fluxo executável com checkpoints persistidos e retomáveis.",
            expected_markers=("WorkflowBuilder", "workflow_checkpoints", "checkpoint_store"),
        ),
        AnalysisTarget(
            target_id="sidecar-artifacts",
            target_name="Markdown/JSON Sidecars",
            target_kind="pipeline_signal",
            scope_group="extraction",
            expected_behavior="O pipeline atual deve gerar e reutilizar artefatos markdown/json no runtime oficial, sem fallback legado externo.",
            expected_markers=("resolve_runtime_artifact_paths", "require_artifacts", ".json", ".md"),
        ),
    ]
