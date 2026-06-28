"""Port for remediation application."""

from __future__ import annotations

from typing import Protocol, Sequence

from faturama.domain.entities.remediation_action import RemediationAction


class RemediationService(Protocol):
    def apply(self, actions: Sequence[RemediationAction]) -> list[RemediationAction]:
        """Apply planned remediations and return their final state."""
