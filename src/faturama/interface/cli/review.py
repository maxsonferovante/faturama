"""CLI commands for review operations."""

from __future__ import annotations

from faturama.application.use_cases.review_queue import list_pending, resolve_item
from faturama.interface.cli.composition import read_model_query_service


def _handle_review_queue(args) -> list[dict]:
    with read_model_query_service() as query_service:
        return list_pending(query_service, args.user_id, args.entity_type, args.status, args.severity)


def _handle_resolve_review(args):
    with read_model_query_service() as query_service:
        return resolve_item(query_service, args.review_item_id, args.resolution, args.note)


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
