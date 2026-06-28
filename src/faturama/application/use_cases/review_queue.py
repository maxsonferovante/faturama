"""Review queue use cases."""

from __future__ import annotations

from pathlib import Path

from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.review_repository import ReviewRepository


def list_pending(
    database_path: str,
    user_id: str,
    entity_type: str | None = None,
    status: str | None = None,
    severity: str | None = None,
) -> list[dict]:
    return ReviewRepository(connect(Path(database_path))).list_review_items_filtered(
        user_id=user_id,
        entity_type=entity_type,
        status=status,
        severity=severity,
    )


def resolve_item(database_path: str, review_item_id: str, resolution: str, note: str | None = None) -> dict:
    repo = ReviewRepository(connect(Path(database_path)))
    existing = repo.get_review_item(review_item_id)
    if not existing:
        return {"error_code": "review_not_found", "message": "Review item not found"}, 1
    if existing["status"] == "resolved":
        return {"error_code": "review_already_resolved", "message": "Review item already resolved"}, 1
    repo.resolve_review_item(
        review_item_id,
        f"{resolution}: {note or ''}".strip(),
        resolution_payload={"resolution": resolution, "note": note},
    )
    return {
        "review_item_id": review_item_id,
        "status": "resolved",
        "resolution": resolution,
        "resume_required": True,
    }
