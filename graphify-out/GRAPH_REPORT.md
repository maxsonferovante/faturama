# Graph Report - .  (2026-07-07)

## Corpus Check
- 269 files · ~105,954 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 684 nodes · 951 edges · 65 communities (40 shown, 25 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 228 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Workflow Builder & Execution
- Ports & Protocols
- PostgreSQL Read-Side Queries
- Logging & Observability
- Object Storage Port
- Installment & Spend Queries
- Lifecycle & Status Services
- Application DTOs
- Reprocessing & Command DTOs
- Document & Statement Repositories
- Domain Exceptions
- Review Repository Adapter
- Installment Persistence Adapter
- Bash Utilities
- Transaction Repository Adapter
- Integration Tests & Concurrency
- Upload Grant Persistence
- Invoice Header Extraction
- Postgres Checkpoint Store
- Postgres Unit of Work
- Test Mocking & Helpers
- Ambiguity Resolution Tests
- Decision Records Repository
- Local Dev Runtime Setup
- Summary Repository Adapter
- Docker Compose Config
- Monthly Spend Summarization
- LangGraph Postgres Checkpointer
- Branch Name Sanitization
- Future Installment Projections
- Transaction Parsing & Extraction
- UOW Factory Adapter
- Review Context Loading
- Installment Matching Logic
- Issuer Detector Service
- Confidence Score Domain Model
- Money Value Object
- Database Schema Management
- PDF Discovery Script
- Document Section Segmentation
- Faturama Package Shim
- Agent Context Update Script
- Prerequisites Verification Script
- Setup Plan Script
- Setup Tasks Script
- DTO Module Init
- Ports Module Init
- Services Module Init
- Use Cases Module Init
- Domain Entities Init
- Domain Services Init
- Value Objects Init
- AWS Infrastructure Adapters
- Checkpoint Adapters Init
- Messaging Adapters Init
- Worker Interface Init
- Project Entrypoint Init
- OCR LLM Verification Script

## God Nodes (most connected - your core abstractions)
1. `process_invoice()` - 35 edges
2. `connect()` - 26 edges
3. `ReadModelQueryService` - 22 edges
4. `DatabaseConfigurationError` - 17 edges
5. `write_async_source()` - 17 edges
6. `load_settings()` - 15 edges
7. `PostgresUnitOfWork` - 15 edges
8. `BaseModel` - 15 edges
9. `process_processing_command()` - 14 edges
10. `InstallmentRepository` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_resolve_auto_applies_when_agent_confidence_reaches_high_threshold()` --calls--> `resolve()`  [INFERRED]
  tests/unit/test_ambiguity_resolution.py → src/faturama/application/services/ambiguity_resolution.py
- `test_resolve_routes_to_human_review_when_agent_confidence_is_not_enough()` --calls--> `resolve()`  [INFERRED]
  tests/unit/test_ambiguity_resolution.py → src/faturama/application/services/ambiguity_resolution.py
- `test_resolve_skips_agent_when_confidence_is_already_high()` --calls--> `resolve()`  [INFERRED]
  tests/unit/test_ambiguity_resolution.py → src/faturama/application/services/ambiguity_resolution.py
- `test_review_workflow_lists_and_resolves_low_confidence_items()` --calls--> `read_model_query_service()`  [INFERRED]
  tests/integration/test_review_workflow.py → src/faturama/application/services/query_service.py
- `test_out_of_order_event_delivery_produces_distinct_dedupe_key()` --calls--> `build_dedupe_key()`  [INFERRED]
  tests/integration/test_source_event_ordering.py → src/faturama/application/services/source_event_normalizer.py

## Import Cycles
- None detected.

## Communities (65 total, 25 thin omitted)

### Community 0 - "Workflow Builder & Execution"
Cohesion: 0.06
Nodes (29): Workflow builder and execution helpers., WorkflowBuilder, _decode_resolution_payload(), make_classify_transactions_node(), make_extract_document_node(), make_finalize_job_node(), make_parse_statement_node(), make_persist_canonical_data_node() (+21 more)

### Community 1 - "Ports & Protocols"
Cohesion: 0.07
Nodes (18): Protocol, ArtifactManifestRepositoryPort, Any, Port for async artifact manifest persistence., CheckpointStore, Any, Workflow checkpoint store port., ExtractionService (+10 more)

### Community 2 - "PostgreSQL Read-Side Queries"
Cohesion: 0.09
Nodes (20): Any, Application read-side query service for PostgreSQL-backed read model., Read-side service assembled at the application boundary for querying the databas, read_model_query_service(), ReadModelQueryService, require_database_dsn(), load_settings(), Application settings. (+12 more)

### Community 3 - "Logging & Observability"
Cohesion: 0.09
Nodes (20): Logger, LogRecord, ProcessingStatusRepository, Any, main(), CLI entrypoint for async worker messages., Worker runtime that validates and executes async processing messages., run_processing_message() (+12 more)

### Community 4 - "Object Storage Port"
Cohesion: 0.07
Nodes (15): ObjectStorage, Path, Port for object storage interactions., build_artifact_key_prefix(), Deterministic artifact-key helpers., ArtifactManifestService, _checksum(), Path (+7 more)

### Community 5 - "Installment & Spend Queries"
Cohesion: 0.07
Nodes (21): Any, QueryService, execute(), Current installments query., execute(), Future installments query., execute(), parse_period() (+13 more)

### Community 6 - "Lifecycle & Status Services"
Cohesion: 0.09
Nodes (17): lifecycle_event_payload(), Helpers for lifecycle transitions and status projections., status_projection_payload(), utc_now(), ProcessingStatusService, Service helpers around status transitions., _connection(), process_processing_command() (+9 more)

### Community 7 - "Application DTOs"
Cohesion: 0.07
Nodes (19): DecisionRecordDTO, Decision record DTOs., DocumentDTO, InstallmentPlanDTO, Installment plan DTOs., ProcessingStatusDTO, DTOs for async status projection and artifacts., ProjectionDTO (+11 more)

### Community 8 - "Reprocessing & Command DTOs"
Cohesion: 0.08
Nodes (19): ProcessingCommandDTO, DTOs for the async processing command contract., Reprocessing helpers., reconcile(), should_ignore_source_delivery(), build_dedupe_key(), _eventbridge_processing_id(), normalize_source_event() (+11 more)

### Community 9 - "Document & Statement Repositories"
Cohesion: 0.10
Nodes (11): DocumentRepository, Document repository port., Statement repository port., StatementRepository, InvoiceStatement, Invoice statement entity., RawDocument, Any (+3 more)

### Community 10 - "Domain Exceptions"
Cohesion: 0.13
Nodes (22): Exception, ArtifactNotFoundError, FaturamaError, ParsingError, Domain-specific exceptions., Raised when extracted artifacts cannot be found., Raised when a document cannot be parsed safely., Raised when manual review is required to proceed. (+14 more)

### Community 11 - "Review Repository Adapter"
Cohesion: 0.10
Nodes (9): Review repository port., ReviewRepository, ReviewItem, evaluate_transaction(), Confidence policy service., Any, Review repository implementation., ReviewRepository (+1 more)

### Community 12 - "Installment Persistence Adapter"
Cohesion: 0.13
Nodes (9): InstallmentRepository, Installment repository port., FutureInstallmentProjection, Future installment projection entity., InstallmentPlan, Installment plan entity., InstallmentRepository, Any (+1 more)

### Community 13 - "Bash Utilities"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 14 - "Transaction Repository Adapter"
Cohesion: 0.14
Nodes (7): Transaction repository port., TransactionRepository, Transaction line entity., TransactionLine, Any, Transaction repository implementation., TransactionRepository

### Community 15 - "Integration Tests & Concurrency"
Cohesion: 0.17
Nodes (10): connect(), connect_from_dsn(), Any, Connection, PostgreSQL connection and unit-of-work helpers., test_processing_status_read_model_contract(), test_first_time_ingestion_is_idempotent(), test_langgraph_workflow_persists_checkpoint_history() (+2 more)

### Community 16 - "Upload Grant Persistence"
Cohesion: 0.21
Nodes (4): Any, UploadGrantRepository, test_signed_upload_grant_can_be_persisted_and_marked_used(), test_s3_event_is_normalized_and_saved()

### Community 17 - "Invoice Header Extraction"
Cohesion: 0.22
Nodes (7): extract_header(), _find_amount(), _find_date(), Header extraction service., extract_card_last4(), Issuer and layout registry., test_extract_header_from_markdown()

### Community 18 - "Postgres Checkpoint Store"
Cohesion: 0.22
Nodes (5): PostgresCheckpointStore, Any, Connection, PostgreSQL-backed workflow checkpoint persistence., test_checkpoint_store_can_save_and_restore()

### Community 19 - "Postgres Unit of Work"
Cohesion: 0.20
Nodes (4): PostgresUnitOfWork, EvidenceRepository, Any, Evidence repository implementation.

### Community 20 - "Test Mocking & Helpers"
Cohesion: 0.31
Nodes (8): async_settings(), async_storage_root(), invoice_dir(), postgres_dsn(), postgres_env(), MonkeyPatch, Path, write_invoice()

### Community 21 - "Ambiguity Resolution Tests"
Cohesion: 0.24
Nodes (7): Validated ambiguity resolution service., resolve(), extract_ambiguous_line(), Structured extraction fallback stub.  The v1 implementation keeps LLM usage opti, test_resolve_auto_applies_when_agent_confidence_reaches_high_threshold(), test_resolve_routes_to_human_review_when_agent_confidence_is_not_enough(), test_resolve_skips_agent_when_confidence_is_already_high()

### Community 22 - "Decision Records Repository"
Cohesion: 0.22
Nodes (4): DecisionRepository, Any, Decision record repository implementation., test_decision_repository_persists_payload()

### Community 23 - "Local Dev Runtime Setup"
Cohesion: 0.46
Nodes (7): ensure_buckets(), list_relevant_artifacts(), list_worker_containers(), log_progress(), main(), read_container_logs(), read_ministack_logs()

### Community 24 - "Summary Repository Adapter"
Cohesion: 0.25
Nodes (3): Any, Summary repository implementation., SummaryRepository

### Community 25 - "Docker Compose Config"
Cohesion: 0.33
Nodes (5): COMPOSE_PROJECT_NAME, MINISTACK_PORT, bootstrap_local_runtime.sh script, TF_VAR_local_aws_endpoint_url, TF_VAR_local_container_aws_endpoint_url

### Community 26 - "Monthly Spend Summarization"
Cohesion: 0.40
Nodes (4): build_summary(), Monthly summary calculations., _sum_amounts(), test_build_summary_splits_new_purchase_and_installments()

### Community 29 - "Future Installment Projections"
Cohesion: 0.40
Nodes (3): project_future_installments(), Future installment projections., test_project_future_installments_rolls_months_forward()

### Community 30 - "Transaction Parsing & Extraction"
Cohesion: 0.40
Nodes (3): extract_candidates(), Transaction candidate extraction., test_extract_candidates_ignores_header_lines()

### Community 32 - "Review Context Loading"
Cohesion: 0.60
Nodes (4): _load_from_runtime_artifacts(), _load_langchain_loader(), load_review_context(), Review context loading for ambiguous cases.

### Community 33 - "Installment Matching Logic"
Cohesion: 0.67
Nodes (3): build_plan(), canonical_key(), Installment matching service.

### Community 34 - "Issuer Detector Service"
Cohesion: 0.67
Nodes (3): detect(), detect_issuer(), Issuer detector service.

### Community 37 - "Database Schema Management"
Cohesion: 0.50
Nodes (3): initialize_schema(), Any, Database schema management.

## Knowledge Gaps
- **13 isolated node(s):** `update-agent-context.sh script`, `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `process_invoice()` connect `Workflow Builder & Execution` to `PostgreSQL Read-Side Queries`, `Logging & Observability`, `Installment & Spend Queries`, `Lifecycle & Status Services`, `Document & Statement Repositories`, `Review Repository Adapter`, `Installment Persistence Adapter`, `Transaction Repository Adapter`, `Integration Tests & Concurrency`, `Postgres Unit of Work`, `Decision Records Repository`, `Summary Repository Adapter`, `LangGraph Postgres Checkpointer`?**
  _High betweenness centrality (0.197) - this node is a cross-community bridge._
- **Why does `process_processing_command()` connect `Lifecycle & Status Services` to `Workflow Builder & Execution`, `PostgreSQL Read-Side Queries`, `Logging & Observability`, `Object Storage Port`, `Reprocessing & Command DTOs`, `Document & Statement Repositories`?**
  _High betweenness centrality (0.169) - this node is a cross-community bridge._
- **Why does `ProcessingCommandDTO` connect `Reprocessing & Command DTOs` to `Lifecycle & Status Services`, `Application DTOs`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `process_invoice()` (e.g. with `InstallmentRepository` and `ReviewRepository`) actually correct?**
  _`process_invoice()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `connect()` (e.g. with `process_invoice()` and `_connection()`) actually correct?**
  _`connect()` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `ReadModelQueryService` (e.g. with `InstallmentRepository` and `ReviewRepository`) actually correct?**
  _`ReadModelQueryService` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `DatabaseConfigurationError` (e.g. with `load_settings()` and `Settings`) actually correct?**
  _`DatabaseConfigurationError` has 13 INFERRED edges - model-reasoned connections that need verification._