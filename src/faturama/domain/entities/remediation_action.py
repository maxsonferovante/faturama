"""Remediation action entity."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RemediationAction:
    action_id: str
    deviation_id: str
    action_type: str
    action_status: str
    action_summary: str
    change_targets: tuple[str, ...] = field(default_factory=tuple)
    requires_manual_followup: bool = False
    patch_path: str | None = None
    original_snippet: str | None = None
    replacement_snippet: str | None = None
    details: str = ""
