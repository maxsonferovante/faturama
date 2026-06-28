"""Workflow builder and execution helpers."""

from __future__ import annotations

from dataclasses import asdict

from langgraph.graph import END, START, StateGraph

from faturama.application.services.workflow_state import WorkflowState


class WorkflowBuilder:
    def __init__(self) -> None:
        self.graph = StateGraph(dict)

    def add_node(self, name: str, handler) -> None:
        self.graph.add_node(name, handler)

    def add_edge(self, source: str, target: str) -> None:
        self.graph.add_edge(source, target)

    def add_default_flow(self) -> None:
        self.graph.add_edge(START, "extract_document")
        self.graph.add_edge("extract_document", "parse_statement")
        self.graph.add_edge("parse_statement", "classify_transactions")
        self.graph.add_edge("classify_transactions", "resolve_ambiguities")
        self.graph.add_edge("resolve_ambiguities", "persist_canonical_data")
        self.graph.add_edge("persist_canonical_data", "finalize_job")
        self.graph.add_edge("finalize_job", END)

    def compile(self, *, checkpointer=None, interrupt_after: list[str] | None = None):
        return self.graph.compile(checkpointer=checkpointer, interrupt_after=interrupt_after)

    @staticmethod
    def to_state_payload(state: WorkflowState) -> dict:
        return asdict(state)
