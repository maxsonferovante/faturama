"""CLI commands for read model queries."""

from __future__ import annotations

from faturama.application.queries import (
    current_installments,
    future_installments,
    list_statements,
    list_transactions,
    monthly_spend,
    remaining_balance,
    show_statement,
)
from faturama.interface.cli.composition import read_model_query_service


def _handle_list_statements(args) -> list[dict]:
    with read_model_query_service() as query_service:
        return list_statements.execute(query_service, args.user_id, args.card, args.from_period, args.to_period)


def _handle_show_statement(args) -> dict | tuple[dict, int]:
    with read_model_query_service() as query_service:
        payload = show_statement.execute(query_service, args.statement_id)
    if payload is None:
        return {"error_code": "statement_not_found", "message": "Statement not found"}, 1
    return payload


def _handle_list_transactions(args) -> list[dict]:
    with read_model_query_service() as query_service:
        return list_transactions.execute(
            query_service,
            args.statement_id,
            kind=args.kind,
            installments_only=args.installments_only,
            review_status=args.review_status,
        )


def _handle_monthly_spend(args) -> list[dict]:
    with read_model_query_service() as query_service:
        return monthly_spend.execute(query_service, args.user_id, args.month, args.card)


def _handle_current_installments(args) -> list[dict]:
    with read_model_query_service() as query_service:
        return current_installments.execute(query_service, args.user_id, args.month, args.card)


def _handle_future_installments(args) -> list[dict]:
    with read_model_query_service() as query_service:
        return future_installments.execute(query_service, args.user_id, args.month, args.card)


def _handle_remaining_balance(args) -> list[dict]:
    with read_model_query_service() as query_service:
        return remaining_balance.execute(query_service, args.user_id, args.card, args.plan_id)


def register_query_commands(subparsers) -> None:
    parser = subparsers.add_parser("list-statements")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--card")
    parser.add_argument("--from", dest="from_period")
    parser.add_argument("--to", dest="to_period")
    parser.add_argument("--format", default="json")
    parser.set_defaults(handler=_handle_list_statements)

    parser = subparsers.add_parser("show-statement")
    parser.add_argument("--statement-id", required=True)
    parser.add_argument("--format", default="json")
    parser.set_defaults(handler=_handle_show_statement)

    parser = subparsers.add_parser("list-transactions")
    parser.add_argument("--statement-id", required=True)
    parser.add_argument("--kind")
    parser.add_argument("--installments-only", action="store_true")
    parser.add_argument("--review-status")
    parser.add_argument("--format", default="json")
    parser.set_defaults(handler=_handle_list_transactions)

    parser = subparsers.add_parser("monthly-spend")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--month", required=True)
    parser.add_argument("--card")
    parser.add_argument("--format", default="json")
    parser.set_defaults(handler=_handle_monthly_spend)

    parser = subparsers.add_parser("current-installments")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--month", required=True)
    parser.add_argument("--card")
    parser.add_argument("--format", default="json")
    parser.set_defaults(handler=_handle_current_installments)

    parser = subparsers.add_parser("future-installments")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--month", required=True)
    parser.add_argument("--card")
    parser.add_argument("--format", default="json")
    parser.set_defaults(handler=_handle_future_installments)

    parser = subparsers.add_parser("remaining-balance")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--card")
    parser.add_argument("--plan-id")
    parser.add_argument("--format", default="json")
    parser.set_defaults(handler=_handle_remaining_balance)
