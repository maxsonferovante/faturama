"""CLI commands for review operations."""

from __future__ import annotations

from faturama.application.use_cases.review_queue import list_pending, resolve_item
from faturama.infrastructure.config.settings import load_settings


def _db_path() -> str:
    return str(load_settings().database_path)


def _handle_review_queue(args) -> list[dict]:
    return list_pending(_db_path(), args.user_id, args.entity_type, args.status, args.severity)


def _handle_resolve_review(args):
    return resolve_item(_db_path(), args.review_item_id, args.resolution, args.note)


def register_review_commands(subparsers) -> None:
    parser = subparsers.add_parser("review-queue")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--entity-type")
    parser.add_argument("--status")
    parser.add_argument("--severity")
    parser.add_argument("--format", default="json")
    parser.set_defaults(handler=_handle_review_queue)

    parser = subparsers.add_parser("resolve-review")
    parser.add_argument("--review-item-id", required=True)
    parser.add_argument("--resolution", required=True)
    parser.add_argument("--note")
    parser.add_argument("--payload-file")
    parser.set_defaults(handler=_handle_resolve_review)
