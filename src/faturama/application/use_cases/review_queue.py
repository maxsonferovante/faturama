"""Review queue use cases."""

from __future__ import annotations

from faturama.application.ports.query_service import QueryService


def list_pending(
    query_service: QueryService,
    user_id: str,
    entity_type: str | None = None,
    status: str | None = None,
    severity: str | None = None,
) -> list[dict]:
    return query_service.query(
        "list_review_items",
        user_id=user_id,
        entity_type=entity_type,
        status=status,
        severity=severity,
    )


def resolve_item(
    query_service: QueryService,
    review_item_id: str,
    resolution: str,
    note: str | None = None,
) -> dict | tuple[dict, int]:
    existing = query_service.query("get_review_item", review_item_id=review_item_id)
    if not existing:
        return {"error_code": "review_not_found", "message": "Review item not found"}, 1
    if existing["status"] == "resolved":
        return {"error_code": "review_already_resolved", "message": "Review item already resolved"}, 1
    query_service.query(
        "resolve_review_item",
        review_item_id=review_item_id,
        resolution_note=f"{resolution}: {note or ''}".strip(),
        resolution_payload={"resolution": resolution, "note": note},
    )
    return {
        "review_item_id": review_item_id,
        "status": "resolved",
        "resolution": resolution,
        "resume_required": True,
    }
