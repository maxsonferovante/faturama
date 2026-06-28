"""CLI command for invoice processing."""

from __future__ import annotations

from faturama.application.use_cases.process_invoice import process_invoice
from faturama.infrastructure.config.settings import load_settings


def _handle_process_invoice(args) -> dict:
    settings = load_settings()
    return process_invoice(
        pdf_path=args.pdf_path,
        user_id=args.user_id,
        settings=settings,
        issuer_hint=args.issuer_hint,
        timezone=args.timezone,
        currency=args.currency,
    )


def _handle_process_batch(args) -> dict:
    from pathlib import Path

    settings = load_settings()
    processed = 0
    succeeded = 0
    review_required = 0
    partial = 0
    failed = 0
    for pdf in sorted(Path(args.input_dir).glob("*.pdf")):
        processed += 1
        try:
            result = process_invoice(
                pdf_path=str(pdf),
                user_id=args.user_id,
                settings=settings,
                issuer_hint=args.issuer_hint,
            )
            if result["status"] == "review_required":
                review_required += 1
            elif result["status"] == "partial":
                partial += 1
            else:
                succeeded += 1
        except Exception:
            failed += 1
            if args.fail_fast:
                raise
    return {
        "batch_id": f"batch:{args.user_id}",
        "processed": processed,
        "succeeded": succeeded,
        "partial": partial,
        "review_required": review_required,
        "failed": failed,
    }


def register_process_invoice(subparsers) -> None:
    process_parser = subparsers.add_parser("process-invoice")
    process_parser.add_argument("--pdf-path", required=True)
    process_parser.add_argument("--user-id", required=True)
    process_parser.add_argument("--issuer-hint")
    process_parser.add_argument("--currency", default="BRL")
    process_parser.add_argument("--timezone", default="America/Sao_Paulo")
    process_parser.set_defaults(handler=_handle_process_invoice)

    batch_parser = subparsers.add_parser("process-batch")
    batch_parser.add_argument("--input-dir", required=True)
    batch_parser.add_argument("--user-id", required=True)
    batch_parser.add_argument("--issuer-hint")
    batch_parser.add_argument("--fail-fast", action="store_true")
    batch_parser.set_defaults(handler=_handle_process_batch)
