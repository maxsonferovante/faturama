"""Review repository implementation."""

from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any

from faturama.domain.entities.review_item import ReviewItem


class ReviewRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def save_review_item(self, item: ReviewItem) -> None:
        payload = asdict(item)
        columns = list(payload.keys())
        values = tuple(payload[column] for column in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        self.connection.execute(
            f"""
            INSERT INTO review_items ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT (review_item_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                entity_type = EXCLUDED.entity_type,
                entity_id = EXCLUDED.entity_id,
                reason_code = EXCLUDED.reason_code,
                reason_detail = EXCLUDED.reason_detail,
                confidence_threshold_snapshot = EXCLUDED.confidence_threshold_snapshot,
                severity = EXCLUDED.severity,
                status = EXCLUDED.status,
                resolution_note = EXCLUDED.resolution_note
            """,
            values,
        )

    def list_review_items(self, user_id: str) -> list[ReviewItem]:
        rows = self.connection.execute(
            "SELECT * FROM review_items WHERE user_id = %s ORDER BY review_item_id",
            (user_id,),
        ).fetchall()
        return [ReviewItem(**dict(row)) for row in rows]

    def list_review_items_filtered(
        self,
        user_id: str,
        entity_type: str | None = None,
        status: str | None = None,
        severity: str | None = None,
    ) -> list[dict]:
        query = "SELECT * FROM review_items WHERE user_id = %s"
        params: list[object] = [user_id]
        if entity_type:
            query += " AND entity_type = %s"
            params.append(entity_type)
        if status:
            query += " AND status = %s"
            params.append(status)
        if severity:
            query += " AND severity = %s"
            params.append(severity)
        query += " ORDER BY review_item_id"
        rows = self.connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]

    def resolve_review_item(
        self,
        review_item_id: str,
        resolution_note: str,
        resolution_payload: dict | None = None,
    ) -> None:
        self.connection.execute(
            "UPDATE review_items SET status = 'resolved', resolution_note = %s, resolution_payload = %s WHERE review_item_id = %s",
            (
                resolution_note,
                json.dumps(resolution_payload, ensure_ascii=False) if resolution_payload else None,
                review_item_id,
            ),
        )

    def get_review_item(self, review_item_id: str) -> dict | None:
        row = self.connection.execute(
            "SELECT * FROM review_items WHERE review_item_id = %s",
            (review_item_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_resolved_item_for_entity(self, entity_id: str) -> dict | None:
        row = self.connection.execute(
            """
            SELECT * FROM review_items
            WHERE entity_id = %s AND status = 'resolved'
            ORDER BY review_item_id DESC
            LIMIT 1
            """,
            (entity_id,),
        ).fetchone()
        return dict(row) if row else None
