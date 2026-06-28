from __future__ import annotations

from faturama.domain.entities.specification_deviation import SpecificationDeviation
from faturama.domain.services.remediation_policy import is_eligible_for_safe_fix, manual_followup_action
from faturama.domain.value_objects.deviation_severity import DeviationSeverity


def test_is_eligible_for_safe_fix_requires_fixable_flag():
    deviation = SpecificationDeviation(
        deviation_id="dev-1",
        target_id="target",
        expected_statement="expected",
        observed_statement="observed",
        deviation_type="type",
        criticality=DeviationSeverity.MEDIUM,
        is_fixable_automatically=True,
    )
    assert is_eligible_for_safe_fix(deviation) is True


def test_manual_followup_action_marks_manual_requirement():
    deviation = SpecificationDeviation(
        deviation_id="dev-2",
        target_id="target",
        expected_statement="expected",
        observed_statement="observed",
        deviation_type="type",
        criticality=DeviationSeverity.HIGH,
        is_fixable_automatically=False,
    )
    action = manual_followup_action(deviation, "revisar")
    assert action.requires_manual_followup is True
    assert action.action_status == "manual_required"
