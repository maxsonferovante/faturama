"""Policy to decide if a deviation is safely fixable."""

from __future__ import annotations

from faturama.domain.entities.remediation_action import RemediationAction
from faturama.domain.entities.specification_deviation import SpecificationDeviation
from faturama.domain.value_objects.deviation_severity import DeviationSeverity


def is_eligible_for_safe_fix(deviation: SpecificationDeviation) -> bool:
    return deviation.is_fixable_automatically and deviation.criticality in {
        DeviationSeverity.LOW,
        DeviationSeverity.MEDIUM,
    }


def manual_followup_action(deviation: SpecificationDeviation, summary: str) -> RemediationAction:
    return RemediationAction(
        action_id=f"manual:{deviation.deviation_id}",
        deviation_id=deviation.deviation_id,
        action_type="manual_followup",
        action_status="manual_required",
        action_summary=summary,
        change_targets=(),
        requires_manual_followup=True,
    )
