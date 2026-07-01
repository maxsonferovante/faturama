"""PostgreSQL-backed workflow checkpoint persistence."""

from __future__ import annotations

from datetime import UTC, datetime
import json
import uuid
from typing import Any

import psycopg


class PostgresCheckpointStore:
    def __init__(self, connection: psycopg.Connection[Any]) -> None:
        self.connection = connection

    def save(
        self,
        job_id: str,
        thread_id: str,
        node_name: str,
        state: dict[str, Any],
        checkpoint_status: str = "active",
        review_required: bool = False,
    ) -> str:
        checkpoint_id = str(uuid.uuid4())
        self.connection.execute(
            """
            INSERT INTO workflow_checkpoints (
                checkpoint_id, job_id, thread_id, node_name, checkpoint_status,
                state_json, review_required, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                checkpoint_id,
                job_id,
                thread_id,
                node_name,
                checkpoint_status,
                json.dumps(state, ensure_ascii=False),
                review_required,
                datetime.now(UTC).isoformat(),
            ),
        )
        self.connection.commit()
        return checkpoint_id

    def latest(self, job_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            """
            SELECT * FROM workflow_checkpoints
            WHERE job_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (job_id,),
        ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["state"] = json.loads(payload.pop("state_json"))
        return payload

    def mark_restored(self, checkpoint_id: str) -> None:
        self.connection.execute(
            """
            UPDATE workflow_checkpoints
            SET checkpoint_status = 'restored', restored_at = %s
            WHERE checkpoint_id = %s
            """,
            (datetime.now(UTC).isoformat(), checkpoint_id),
        )
        self.connection.commit()
