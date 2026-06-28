"""Workflow state containers."""

from __future__ import annotations

from dataclasses import dataclass, field
import uuid


@dataclass(slots=True)
class WorkflowState:
    pdf_path: str
    user_id: str
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    issuer_hint: str | None = None
    status: str = "initialized"
    partial_status: str = "complete"
    artifacts: dict = field(default_factory=dict)
    statement: dict = field(default_factory=dict)
    transactions: list[dict] = field(default_factory=list)
    plans: list[dict] = field(default_factory=list)
    projections: list[dict] = field(default_factory=list)
    review_items: list[dict] = field(default_factory=list)
    auto_applied_items: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
