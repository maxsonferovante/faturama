"""Helpers to build evidence records from search results."""

from __future__ import annotations

from datetime import UTC, datetime
import uuid

from faturama.application.ports.repository_inspector import SearchHit
from faturama.domain.entities.evidence_record import EvidenceRecord
from faturama.domain.value_objects.evidence_kind import EvidenceKind


def build_evidence(target_id: str, evidence_kind: EvidenceKind, hit: SearchHit, confidence: float) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"evidence:{target_id}:{hit.path}:{hit.line_number}:{evidence_kind.value}")),
        target_id=target_id,
        evidence_kind=evidence_kind,
        source_path=hit.path,
        source_excerpt=hit.excerpt,
        source_line_reference=f"{hit.path}:{hit.line_number}",
        confidence_level=confidence,
        observed_at=datetime.now(UTC).isoformat(),
    )
