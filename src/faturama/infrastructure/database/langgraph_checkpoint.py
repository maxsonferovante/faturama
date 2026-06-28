"""SQLite-backed workflow checkpoint persistence."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import sqlite3
import uuid


class SQLiteCheckpointStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                node_name TEXT NOT NULL,
                checkpoint_status TEXT NOT NULL,
                state_json TEXT NOT NULL,
                review_required INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                restored_at TEXT
            )
            """
        )
        self.connection.commit()

    def save(
        self,
        job_id: str,
        thread_id: str,
        node_name: str,
        state: dict,
        checkpoint_status: str = "active",
        review_required: bool = False,
    ) -> str:
        checkpoint_id = str(uuid.uuid4())
        self.connection.execute(
            """
            INSERT INTO workflow_checkpoints (
                checkpoint_id, job_id, thread_id, node_name, checkpoint_status,
                state_json, review_required, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                checkpoint_id,
                job_id,
                thread_id,
                node_name,
                checkpoint_status,
                json.dumps(state, ensure_ascii=False),
                1 if review_required else 0,
                datetime.now(UTC).isoformat(),
            ),
        )
        self.connection.commit()
        return checkpoint_id

    def latest(self, job_id: str) -> dict | None:
        row = self.connection.execute(
            """
            SELECT * FROM workflow_checkpoints
            WHERE job_id = ?
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
            SET checkpoint_status = 'restored', restored_at = ?
            WHERE checkpoint_id = ?
            """,
            (datetime.now(UTC).isoformat(), checkpoint_id),
        )
        self.connection.commit()


class LangGraphSqliteRuntime:
    def __init__(self, database_path: Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._context_manager = None
        self.checkpointer = None

    def open(self):
        try:
            from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore
        except Exception:
            return None
        self._context_manager = SqliteSaver.from_conn_string(str(self.database_path))
        self.checkpointer = self._context_manager.__enter__()
        return self.checkpointer

    def close(self) -> None:
        if self._context_manager is not None:
            self._context_manager.__exit__(None, None, None)
            self._context_manager = None
            self.checkpointer = None
