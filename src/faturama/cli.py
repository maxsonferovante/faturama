"""Main CLI entrypoint."""

from __future__ import annotations

import argparse
import json

from faturama.interface.cli.process_invoice import register_process_invoice
from faturama.interface.cli.queries import register_query_commands
from faturama.interface.cli.review import register_review_commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="faturama")
    subparsers = parser.add_subparsers(dest="command", required=True)
    register_process_invoice(subparsers)
    register_query_commands(subparsers)
    register_review_commands(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = args.handler(args)
    if isinstance(payload, tuple):
        body, exit_code = payload
    else:
        body, exit_code = payload, 0

    if isinstance(body, (dict, list)):
        print(json.dumps(body, ensure_ascii=False, indent=2))
    elif body is not None:
        print(body)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
