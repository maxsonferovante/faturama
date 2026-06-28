"""Decision record repository implementation."""

from __future__ import annotations

import json
from sqlite3 import Connection


class DecisionRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def save_decision(self, payload: dict) -> None:
        payload = dict(payload)
        payload.setdefault("decision_source", "rule")
        payload.setdefault("audit_payload", None)
        audit_payload = payload.get("audit_payload")
        if isinstance(audit_payload, (dict, list)):
            payload["audit_payload"] = json.dumps(audit_payload, ensure_ascii=False)
        self.connection.execute(
            """
            INSERT OR REPLACE INTO decision_records (
                decision_id, entity_type, entity_id, decision_state, confidence_structural,
                confidence_semantic, confidence_relational, confidence_operational, decision_reason,
                decision_source, audit_payload
            ) VALUES (
                :decision_id, :entity_type, :entity_id, :decision_state, :confidence_structural,
                :confidence_semantic, :confidence_relational, :confidence_operational, :decision_reason,
                :decision_source, :audit_payload
            )
            """,
            payload,
        )
        self.connection.commit()

    def list_decisions(self, entity_type: str, entity_id: str) -> list[dict]:
        rows = self.connection.execute(
            "SELECT * FROM decision_records WHERE entity_type = ? AND entity_id = ? ORDER BY decision_id",
            (entity_type, entity_id),
        ).fetchall()
        return [dict(row) for row in rows]
