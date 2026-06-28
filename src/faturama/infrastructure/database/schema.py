"""Database schema management."""

from __future__ import annotations

from sqlite3 import Connection


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS documents (
        document_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        source_pdf_path TEXT NOT NULL,
        file_hash TEXT NOT NULL UNIQUE,
        raw_markdown_path TEXT,
        raw_json_path TEXT,
        issuer_hint TEXT,
        detected_issuer TEXT,
        layout_family TEXT,
        extraction_version TEXT,
        page_count INTEGER,
        runtime_source TEXT NOT NULL DEFAULT 'legacy',
        legacy_status TEXT NOT NULL DEFAULT 'invalidated',
        partial_status TEXT NOT NULL DEFAULT 'complete'
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS statements (
        statement_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        issuer_name TEXT,
        card_fingerprint TEXT NOT NULL,
        billing_year INTEGER NOT NULL,
        billing_month INTEGER NOT NULL,
        statement_status TEXT NOT NULL,
        parse_confidence REAL NOT NULL,
        card_label TEXT,
        card_last4 TEXT,
        card_holder_name TEXT,
        statement_due_date TEXT,
        statement_close_date TEXT,
        statement_issue_date TEXT,
        statement_total_amount TEXT,
        minimum_payment_amount TEXT,
        credit_limit_amount TEXT,
        currency TEXT NOT NULL,
        runtime_source TEXT NOT NULL DEFAULT 'legacy',
        legacy_status TEXT NOT NULL DEFAULT 'invalidated',
        partial_status TEXT NOT NULL DEFAULT 'complete'
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS evidences (
        evidence_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        page_number INTEGER,
        raw_text TEXT NOT NULL,
        bbox TEXT,
        json_node_ref TEXT,
        extraction_method TEXT NOT NULL,
        structural_confidence REAL NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id TEXT PRIMARY KEY,
        statement_id TEXT NOT NULL,
        document_id TEXT NOT NULL,
        card_fingerprint TEXT NOT NULL,
        description_raw TEXT NOT NULL,
        amount TEXT NOT NULL,
        transaction_kind TEXT NOT NULL,
        line_hash TEXT NOT NULL,
        parse_confidence REAL NOT NULL,
        review_status TEXT NOT NULL,
        decision_state TEXT NOT NULL,
        source_evidence_id TEXT,
        source_strategy TEXT NOT NULL,
        currency TEXT NOT NULL,
        posted_date TEXT,
        purchase_date TEXT,
        description_normalized TEXT,
        merchant_normalized TEXT,
        raw_text TEXT,
        page_number INTEGER,
        is_installment INTEGER NOT NULL,
        installment_current INTEGER,
        installment_total INTEGER,
        UNIQUE(statement_id, line_hash)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS installment_plans (
        installment_plan_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        card_fingerprint TEXT NOT NULL,
        installment_type TEXT NOT NULL,
        description_anchor TEXT NOT NULL,
        description_normalized TEXT NOT NULL,
        merchant_normalized TEXT,
        origin_purchase_date TEXT,
        installment_amount TEXT NOT NULL,
        installment_total INTEGER NOT NULL,
        first_seen_statement_id TEXT,
        last_seen_statement_id TEXT,
        plan_status TEXT NOT NULL,
        plan_confidence REAL NOT NULL,
        matching_strategy TEXT NOT NULL,
        canonical_key TEXT NOT NULL UNIQUE,
        runtime_source TEXT NOT NULL DEFAULT 'legacy',
        legacy_status TEXT NOT NULL DEFAULT 'invalidated'
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS projections (
        projection_id TEXT PRIMARY KEY,
        installment_plan_id TEXT NOT NULL,
        card_fingerprint TEXT NOT NULL,
        projected_billing_year INTEGER NOT NULL,
        projected_billing_month INTEGER NOT NULL,
        projected_installment_number INTEGER NOT NULL,
        projected_amount TEXT NOT NULL,
        projection_status TEXT NOT NULL,
        projection_confidence REAL NOT NULL,
        UNIQUE(installment_plan_id, projected_billing_year, projected_billing_month, projected_installment_number)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS summaries (
        summary_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        card_fingerprint TEXT NOT NULL,
        issuer_name TEXT,
        card_label TEXT,
        billing_year INTEGER NOT NULL,
        billing_month INTEGER NOT NULL,
        statement_total_amount TEXT,
        new_purchase_total TEXT,
        installment_charge_total TEXT,
        invoice_financing_total TEXT,
        interest_and_fees_total TEXT,
        refund_total TEXT,
        future_installment_balance TEXT,
        next_cycle_installment_commitment TEXT,
        runtime_source TEXT NOT NULL DEFAULT 'legacy',
        legacy_status TEXT NOT NULL DEFAULT 'invalidated',
        UNIQUE(user_id, card_fingerprint, billing_year, billing_month)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS review_items (
        review_item_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        reason_code TEXT NOT NULL,
        reason_detail TEXT NOT NULL,
        confidence_threshold_snapshot REAL NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        resolution_note TEXT,
        resolution_payload TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS decision_records (
        decision_id TEXT PRIMARY KEY,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        decision_state TEXT NOT NULL,
        confidence_structural REAL NOT NULL,
        confidence_semantic REAL NOT NULL,
        confidence_relational REAL NOT NULL,
        confidence_operational REAL NOT NULL,
        decision_reason TEXT NOT NULL,
        decision_source TEXT NOT NULL DEFAULT 'rule',
        audit_payload TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_checkpoints (
        checkpoint_id TEXT PRIMARY KEY,
        job_id TEXT NOT NULL,
        thread_id TEXT NOT NULL,
        node_name TEXT NOT NULL,
        checkpoint_status TEXT NOT NULL,
        state_json TEXT NOT NULL,
        review_required INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        restored_at TEXT
    )
    """,
]


def initialize_schema(connection: Connection) -> None:
    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    _apply_compatibility_migrations(connection)
    connection.commit()


def _apply_compatibility_migrations(connection: Connection) -> None:
    _ensure_columns(
        connection,
        "documents",
        {
            "runtime_source": "TEXT NOT NULL DEFAULT 'legacy'",
            "legacy_status": "TEXT NOT NULL DEFAULT 'invalidated'",
            "partial_status": "TEXT NOT NULL DEFAULT 'complete'",
        },
    )
    _ensure_columns(
        connection,
        "statements",
        {
            "runtime_source": "TEXT NOT NULL DEFAULT 'legacy'",
            "legacy_status": "TEXT NOT NULL DEFAULT 'invalidated'",
            "partial_status": "TEXT NOT NULL DEFAULT 'complete'",
        },
    )
    _ensure_columns(
        connection,
        "installment_plans",
        {
            "runtime_source": "TEXT NOT NULL DEFAULT 'legacy'",
            "legacy_status": "TEXT NOT NULL DEFAULT 'invalidated'",
        },
    )
    _ensure_columns(
        connection,
        "summaries",
        {
            "runtime_source": "TEXT NOT NULL DEFAULT 'legacy'",
            "legacy_status": "TEXT NOT NULL DEFAULT 'invalidated'",
        },
    )
    _ensure_columns(
        connection,
        "review_items",
        {
            "resolution_payload": "TEXT",
        },
    )
    _ensure_columns(
        connection,
        "decision_records",
        {
            "decision_source": "TEXT NOT NULL DEFAULT 'rule'",
            "audit_payload": "TEXT",
        },
    )
    _mark_legacy_rows(connection)


def _ensure_columns(connection: Connection, table_name: str, columns: dict[str, str]) -> None:
    existing = {
        row[1]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    for name, definition in columns.items():
        if name not in existing:
            connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {name} {definition}")


def _mark_legacy_rows(connection: Connection) -> None:
    connection.execute(
        """
        UPDATE documents
        SET runtime_source = COALESCE(NULLIF(runtime_source, ''), 'legacy'),
            legacy_status = CASE
                WHEN runtime_source = 'official' THEN legacy_status
                ELSE 'invalidated'
            END
        WHERE runtime_source IS NULL OR runtime_source = '' OR runtime_source != 'official'
        """
    )
    connection.execute(
        """
        UPDATE installment_plans
        SET runtime_source = COALESCE(NULLIF(runtime_source, ''), 'legacy'),
            legacy_status = CASE
                WHEN runtime_source = 'official' THEN legacy_status
                ELSE 'invalidated'
            END
        WHERE runtime_source IS NULL OR runtime_source = '' OR runtime_source != 'official'
        """
    )
    connection.execute(
        """
        UPDATE summaries
        SET runtime_source = COALESCE(NULLIF(runtime_source, ''), 'legacy'),
            legacy_status = CASE
                WHEN runtime_source = 'official' THEN legacy_status
                ELSE 'invalidated'
            END
        WHERE runtime_source IS NULL OR runtime_source = '' OR runtime_source != 'official'
        """
    )
    connection.execute(
        """
        UPDATE statements
        SET runtime_source = COALESCE(NULLIF(runtime_source, ''), 'legacy'),
            legacy_status = CASE
                WHEN runtime_source = 'official' THEN legacy_status
                ELSE 'invalidated'
            END
        WHERE runtime_source IS NULL OR runtime_source = '' OR runtime_source != 'official'
        """
    )
