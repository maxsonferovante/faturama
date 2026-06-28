"""Review repository port."""

from __future__ import annotations

from typing import Protocol

from faturama.domain.entities.review_item import ReviewItem


class ReviewRepository(Protocol):
    def save_review_item(self, item: ReviewItem) -> None: ...
    def list_review_items(self, user_id: str) -> list[ReviewItem]: ...
    def resolve_review_item(self, review_item_id: str, resolution_note: str) -> None: ...
