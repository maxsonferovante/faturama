"""Evidence kind value object."""

from __future__ import annotations

from enum import StrEnum


class EvidenceKind(StrEnum):
    EXECUTABLE_USAGE = "executable_usage"
    EXECUTION_SIGNAL = "execution_signal"
    REINFORCING_TEST = "reinforcing_test"
    DECLARED_DEPENDENCY = "declared_dependency"
    DOCUMENTATION_EXPECTATION = "documentation_expectation"
    NAMING_ONLY = "naming_only"
    STRUCTURAL_SIGNAL = "structural_signal"
