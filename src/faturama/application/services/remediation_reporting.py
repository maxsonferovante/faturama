"""Helpers to present remediation decisions."""

from __future__ import annotations

from faturama.application.dto.remediation_dto import RemediationDTO
from faturama.domain.entities.remediation_action import RemediationAction


def build_remediation_dto(action: RemediationAction, target_id: str) -> RemediationDTO:
    return RemediationDTO(
        action_id=action.action_id,
        deviation_id=action.deviation_id,
        target_id=target_id,
        action_type=action.action_type,
        action_status=action.action_status,
        action_summary=action.action_summary,
        change_targets=list(action.change_targets),
        requires_manual_followup=action.requires_manual_followup,
        details=action.details,
    )
