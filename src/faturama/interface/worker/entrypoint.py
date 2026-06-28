"""CLI entrypoint for async worker messages."""

from __future__ import annotations

import argparse
import json
import sys

from faturama.infrastructure.config.settings import load_settings
from faturama.interface.worker.runner import run_processing_message


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the faturama async worker")
    parser.add_argument("--message", help="JSON processing message payload")
    parser.add_argument("--help-message", action="store_true", help="Show an example payload and exit")
    args = parser.parse_args(argv)

    if args.help_message:
        print(
            json.dumps(
                {
                    "processing_id": "evt-20260628-0001",
                    "bucket": "pre-processamento-faturama",
                    "object_key": "incoming/fatura-2026-04.pdf",
                    "event_time": "2026-06-28T12:00:00Z",
                    "source": "s3",
                    "upload_grant_id": "grant-20260628-001",
                    "metadata": {},
                }
            )
        )
        return 0

    settings = load_settings()
    raw_payload = args.message or settings.processing_message or sys.stdin.read().strip()
    if not raw_payload:
        parser.error("A processing message must be provided via --message, FATURAMA_PROCESSING_MESSAGE, or stdin")
    payload = json.loads(raw_payload)
    result = run_processing_message(payload, settings=settings)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
