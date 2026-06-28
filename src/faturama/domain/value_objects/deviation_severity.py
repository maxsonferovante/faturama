"""Deviation severity value object."""

from __future__ import annotations

from enum import StrEnum


class DeviationSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
