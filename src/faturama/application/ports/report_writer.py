"""Port for report materialization."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from faturama.application.dto.usage_report_dto import UsageReportDTO


class ReportWriter(Protocol):
    def write(self, report: UsageReportDTO, output_path: str | None = None) -> Path:
        """Materialize the report and return the resulting path."""
