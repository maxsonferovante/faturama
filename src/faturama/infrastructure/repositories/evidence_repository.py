"""Evidence repository implementation."""

from __future__ import annotations

import uuid
from sqlite3 import Connection


class EvidenceRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def save_evidence(
        self,
        document_id: str,
        raw_text: str,
        page_number: int | None = None,
        extraction_method: str = "rule",
        structural_confidence: float = 1.0,
    ) -> str:
        evidence_id = str(uuid.uuid4())
        self.connection.execute(
            """
            INSERT INTO evidences (
                evidence_id, document_id, page_number, raw_text, bbox, json_node_ref, extraction_method, structural_confidence
            ) VALUES (?, ?, ?, ?, NULL, NULL, ?, ?)
            """,
            (evidence_id, document_id, page_number, raw_text, extraction_method, structural_confidence),
        )
        self.connection.commit()
        return evidence_id
