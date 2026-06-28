"""Concrete remediation service."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from faturama.application.ports.remediation_service import RemediationService
from faturama.domain.entities.remediation_action import RemediationAction


class FileRemediationService(RemediationService):
    def __init__(self, root: Path) -> None:
        self.root = root

    def apply(self, actions: Sequence[RemediationAction]) -> list[RemediationAction]:
        results: list[RemediationAction] = []
        for action in actions:
            if (
                action.action_status != "planned"
                or not action.patch_path
                or action.original_snippet is None
                or action.replacement_snippet is None
            ):
                results.append(action)
                continue
            target = self.root / action.patch_path
            text = target.read_text(encoding="utf-8")
            if text.count(action.original_snippet) != 1:
                action.action_status = "manual_required"
                action.requires_manual_followup = True
                action.details = "Patch não aplicado: trecho original não é único."
                results.append(action)
                continue
            target.write_text(
                text.replace(action.original_snippet, action.replacement_snippet, 1),
                encoding="utf-8",
            )
            action.action_status = "applied"
            action.details = f"Patch aplicado em {action.patch_path}."
            results.append(action)
        return results
