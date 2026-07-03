"""Decision record repository implementation."""

from __future__ import annotations

import json
from typing import Any


class DecisionRepository:
    def __init__(self, connection: Any) -> None:
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
            INSERT INTO decision_records (
                decision_id, entity_type, entity_id, decision_state, confidence_structural,
                confidence_semantic, confidence_relational, confidence_operational, decision_reason,
                decision_source, audit_payload
            ) VALUES (
                %(decision_id)s, %(entity_type)s, %(entity_id)s, %(decision_state)s, %(confidence_structural)s,
                %(confidence_semantic)s, %(confidence_relational)s, %(confidence_operational)s, %(decision_reason)s,
                %(decision_source)s, %(audit_payload)s
            )
            ON CONFLICT (decision_id) DO UPDATE SET
                entity_type = EXCLUDED.entity_type,
                entity_id = EXCLUDED.entity_id,
                decision_state = EXCLUDED.decision_state,
                confidence_structural = EXCLUDED.confidence_structural,
                confidence_semantic = EXCLUDED.confidence_semantic,
                confidence_relational = EXCLUDED.confidence_relational,
                confidence_operational = EXCLUDED.confidence_operational,
                decision_reason = EXCLUDED.decision_reason,
                decision_source = EXCLUDED.decision_source,
                audit_payload = EXCLUDED.audit_payload
            """,
            payload,
        )

    def list_decisions(self, entity_type: str, entity_id: str) -> list[dict]:
        rows = self.connection.execute(
            "SELECT * FROM decision_records WHERE entity_type = %s AND entity_id = %s ORDER BY decision_id",
            (entity_type, entity_id),
        ).fetchall()
        return [dict(row) for row in rows]
