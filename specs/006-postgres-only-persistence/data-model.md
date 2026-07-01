# Data Model: PostgreSQL Only Persistence

## Overview

A feature não introduz novas entidades de negócio principais; ela redefine o contrato operacional de persistência para que todos os modelos canônicos, read models e checkpoints passem a viver no mesmo PostgreSQL oficial. O impacto de modelagem está em tipos, ownership transacional e lifecycle de bootstrap.

## Canonical Persistence Aggregate

### DocumentRecord

Represents the persisted invoice ingestion root.

**Key fields**:
- `document_id`
- `user_id`
- `source_pdf_path`
- `file_hash`
- `raw_markdown_path`
- `raw_json_path`
- `issuer_hint`
- `detected_issuer`
- `layout_family`
- `extraction_version`
- `page_count`
- `runtime_source`
- `legacy_status`
- `partial_status`

**Rules**:
- `file_hash` remains unique and anchors idempotent reprocessing.
- `runtime_source`, `legacy_status` and `partial_status` remain semantically preserved during migration.
- Persistence occurs inside the same unit of work as statement, transactions, projections and review artifacts.

### StatementRecord

Represents one canonical invoice statement tied to a processed document.

**Key fields**:
- `statement_id`
- `document_id`
- `user_id`
- `issuer_name`
- `card_fingerprint`
- `billing_year`
- `billing_month`
- `statement_status`
- `parse_confidence`
- `statement_due_date`
- `statement_close_date`
- `statement_issue_date`
- `statement_total_amount`
- `minimum_payment_amount`
- `credit_limit_amount`
- `currency`
- `runtime_source`
- `legacy_status`
- `partial_status`

**Rules**:
- Upsert semantics must be explicit in PostgreSQL.
- Read-side filters by card and period must remain available without direct SQL access from callers.

### TransactionRecord

Represents one classified transaction line linked to a statement.

**Key fields**:
- `transaction_id`
- `statement_id`
- `line_hash`
- `transaction_kind`
- `occurred_on`
- `description_raw`
- `merchant_normalized`
- `amount_text`
- `currency`
- `review_status`
- `card_fingerprint`
- `is_installment`
- `runtime_source`
- `legacy_status`

**Rules**:
- `is_installment` becomes a PostgreSQL boolean field.
- Query-by-statement and query-by-month behaviors move behind repository or read-service methods.

### InstallmentPlanRecord

Represents one installment plan and its derived future projections.

**Key fields**:
- `installment_plan_id`
- `user_id`
- `card_fingerprint`
- `description_anchor`
- `installment_total`
- `current_installment`
- `plan_status`
- `runtime_source`
- `legacy_status`

**Rules**:
- Remaining-balance calculation must be exposed via repository/read-service contract, not via direct connection access.
- Deletion and recreation of projections for a plan must run inside the same outer transaction.

### ProjectionRecord

Represents one projected future installment entry.

**Key fields**:
- `projection_id`
- `installment_plan_id`
- `user_id`
- `card_fingerprint`
- `projected_billing_year`
- `projected_billing_month`
- `projected_amount`

**Rules**:
- Monetary text may remain canonical if required for audit fidelity.
- If numeric read columns are introduced for operational calculations, they belong to PostgreSQL read-model design, not to a SQLite compatibility layer.

### SummaryRecord

Represents one monthly summary read model.

**Key fields**:
- `summary_id`
- `user_id`
- `card_fingerprint`
- `billing_year`
- `billing_month`
- `statement_total_amount`
- `new_purchase_total`
- `installment_charge_total`
- `future_installment_balance`
- `next_cycle_installment_commitment`
- `runtime_source`
- `legacy_status`

**Rules**:
- Upsert remains required, but in native PostgreSQL syntax.
- Reads by month remain available through query-facing contracts.

## Operational Persistence Aggregate

### ReviewItemRecord

Represents manual review backlog and resolution state.

**Key fields**:
- `review_item_id`
- `user_id`
- `entity_type`
- `entity_id`
- `status`
- `severity`
- `resolution_note`
- `resolution_payload`

**Rules**:
- The queue and resolution flow must survive removal of all local database paths.
- Review resolution remains queryable through repository or service contracts.

### DecisionRecord

Represents auto-applied or manual decision audit trail.

**Key fields**:
- `decision_id`
- `entity_type`
- `entity_id`
- `decision_state`
- `decision_source`
- `audit_payload`
- confidence dimensions already stored by the current model

**Rules**:
- JSON audit payload remains preserved without SQLite adaptation.

### ProcessingJobRecord

Represents the orchestration lifecycle of one async processing attempt.

**Key fields**:
- `processing_id`
- `source_event_id`
- `execution_arn`
- `dispatch_attempt`
- `current_status`
- `status_detail`
- `bucket_name`
- `object_key`
- `document_id`
- `file_hash`
- `requested_at`
- `started_at`
- `finished_at`
- `failure_code`
- `failure_message`
- `runtime_environment`

**Rules**:
- Creation and status transitions must use PostgreSQL-only repositories and the same DSN as synchronous processing.

### ProcessingStatusRecord

Represents the operational read model consumed by status APIs and diagnostics.

**Key fields**:
- `processing_id`
- `document_id`
- `file_hash`
- `current_status`
- `is_terminal`
- `status_detail`
- `result_reference`
- `artifact_manifest_id`
- `review_required`
- `last_transition_at`
- `updated_at`

**Rules**:
- `is_terminal` and `review_required` become boolean fields.
- Reads by `processing_id` and `file_hash` stay available through port contracts.

### ArtifactManifestRecord

Represents the persisted manifest of generated artifacts.

**Key fields**:
- `artifact_manifest_id`
- `processing_id`
- references to generated objects and result metadata

**Rules**:
- The manifest remains in PostgreSQL, while large artifacts remain in object storage.

### WorkflowCheckpointRecord

Represents resumable workflow state.

**Key fields**:
- `checkpoint_id`
- `job_id`
- `thread_id`
- `node_name`
- `checkpoint_status`
- `state_json`
- `review_required`
- `created_at`
- `restored_at`

**Rules**:
- Checkpoints must be stored in PostgreSQL only.
- `review_required` becomes boolean.
- Operations required by the feature are `save`, `latest(job_id)`, and `mark_restored(checkpoint_id)`.

## Configuration Model

### DatabaseRuntimeConfig

Represents the only supported database configuration contract.

**Key fields**:
- `database_dsn`
- optional explicit bootstrap/migration controls if introduced during implementation

**Rules**:
- `database_dsn` is mandatory.
- SQLite DSNs and local path variables are invalid configuration.
- CLI, worker and tests consume the same DSN model.

## Transaction Boundaries

### InvoiceProcessingUnitOfWork

Coordinates one atomic processing cycle.

**Owns**:
- database connection lifecycle
- begin/commit/rollback
- repository instances for canonical persistence
- checkpoint store access when the workflow stage requires durable state

**Boundary rule**:
- Document, statement, evidence, transactions, installment plans, projections, summaries, review items and decisions for one processing cycle should be committed atomically whenever the use case reaches the persistence stage.

### ReadOnlyQuerySession

Supports CLI and query handlers.

**Owns**:
- read connection lifecycle
- repository or query service methods for statements, transactions, summaries, projections, balances and review queue

**Boundary rule**:
- Callers do not access raw connection objects directly.
