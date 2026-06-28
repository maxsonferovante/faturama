"""DTOs for remediation actions."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RemediationDTO:
    action_id: str
    deviation_id: str
    target_id: str
    action_type: str
    action_status: str
    action_summary: str
    change_targets: list[str] = field(default_factory=list)
    requires_manual_followup: bool = False
    details: str = ""
