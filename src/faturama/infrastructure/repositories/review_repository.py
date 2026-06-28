"""Review repository implementation."""

from __future__ import annotations

from dataclasses import asdict
import json
from sqlite3 import Connection

from faturama.domain.entities.review_item import ReviewItem


class ReviewRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def save_review_item(self, item: ReviewItem) -> None:
        self.connection.execute(
            """
            INSERT OR REPLACE INTO review_items (
                review_item_id, user_id, entity_type, entity_id, reason_code, reason_detail,
                confidence_threshold_snapshot, severity, status, resolution_note
            ) VALUES (
                :review_item_id, :user_id, :entity_type, :entity_id, :reason_code, :reason_detail,
                :confidence_threshold_snapshot, :severity, :status, :resolution_note
            )
            """,
            asdict(item),
        )
        self.connection.commit()

    def list_review_items(self, user_id: str) -> list[ReviewItem]:
        rows = self.connection.execute(
            "SELECT * FROM review_items WHERE user_id = ? ORDER BY review_item_id", (user_id,)
        ).fetchall()
        return [ReviewItem(**dict(row)) for row in rows]

    def list_review_items_filtered(
        self,
        user_id: str,
        entity_type: str | None = None,
        status: str | None = None,
        severity: str | None = None,
    ) -> list[dict]:
        query = "SELECT * FROM review_items WHERE user_id = ?"
        params: list[object] = [user_id]
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        query += " ORDER BY review_item_id"
        rows = self.connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]

    def resolve_review_item(self, review_item_id: str, resolution_note: str, resolution_payload: dict | None = None) -> None:
        self.connection.execute(
            "UPDATE review_items SET status = 'resolved', resolution_note = ?, resolution_payload = ? WHERE review_item_id = ?",
            (
                resolution_note,
                json.dumps(resolution_payload, ensure_ascii=False) if resolution_payload else None,
                review_item_id,
            ),
        )
        self.connection.commit()

    def get_review_item(self, review_item_id: str) -> dict | None:
        row = self.connection.execute(
            "SELECT * FROM review_items WHERE review_item_id = ?",
            (review_item_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_resolved_item_for_entity(self, entity_id: str) -> dict | None:
        row = self.connection.execute(
            """
            SELECT * FROM review_items
            WHERE entity_id = ? AND status = 'resolved'
            ORDER BY review_item_id DESC
            LIMIT 1
            """,
            (entity_id,),
        ).fetchone()
        return dict(row) if row else None
