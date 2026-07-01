from __future__ import annotations

from faturama.infrastructure.database.postgres import connect
from faturama.infrastructure.repositories.decision_repository import DecisionRepository


def test_decision_repository_persists_payload(temp_db):
    connection = connect(temp_db)
    try:
        repo = DecisionRepository(connection)
        repo.save_decision(
            {
                "decision_id": "d1",
                "entity_type": "transaction",
                "entity_id": "tx-1",
                "decision_state": "accepted_medium",
                "confidence_structural": 0.9,
                "confidence_semantic": 0.9,
                "confidence_relational": 1.0,
                "confidence_operational": 0.9,
                "decision_reason": "test",
            }
        )
        assert repo.list_decisions("transaction", "tx-1")[0]["decision_id"] == "d1"
    finally:
        connection.close()

