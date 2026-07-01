# Tasks: PostgreSQL Only Persistence

**Input**: Design documents from `/specs/006-postgres-only-persistence/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks are included because the feature explicitly requires PostgreSQL-backed validation for processing, CLI reads, checkpoints, configuration failure, and local runtime behavior.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Remove obsolete dependencies and prepare the PostgreSQL-only working surface.

- [x] T001 Remove the SQLite-only runtime dependency from `pyproject.toml`
- [x] T002 [P] Create the PostgreSQL migration/bootstrap module layout in `src/faturama/infrastructure/database/` and `src/faturama/infrastructure/checkpoint/`
- [x] T003 [P] Add PostgreSQL-backed test environment helpers for local containers in `tests/conftest.py` and `tests/async_helpers.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the PostgreSQL-only foundation that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Delete the legacy SQLite connector module `src/faturama/infrastructure/database/sqlite.py` and remove its imports from productive code
- [x] T005 Replace compatibility-oriented connection handling with native PostgreSQL connection lifecycle in `src/faturama/infrastructure/database/postgres.py`
- [x] T006 Replace SQLite-oriented schema bootstrap and compatibility migration logic with PostgreSQL-native bootstrap in `src/faturama/infrastructure/database/schema.py`
- [x] T007 Introduce unit-of-work and checkpoint-store application ports in `src/faturama/application/ports/`
- [x] T008 Create PostgreSQL-backed unit-of-work and repository provider composition in `src/faturama/infrastructure/database/` and `src/faturama/interface/`
- [x] T009 Create a real PostgreSQL checkpoint store and runtime integration in `src/faturama/infrastructure/checkpoint/postgres_checkpoint_store.py` and `src/faturama/infrastructure/database/langgraph_checkpoint.py`
- [x] T010 Remove legacy database path settings and enforce PostgreSQL DSN validation in `src/faturama/infrastructure/config/settings.py`
- [x] T011 [P] Update shared repository constructors to stop depending on `sqlite3.Connection` in `src/faturama/infrastructure/repositories/`
- [x] T012 [P] Add foundational integration coverage for DSN validation and PostgreSQL bootstrap in `tests/integration/test_settings.py` and `tests/integration/test_postgres_bootstrap.py`

**Checkpoint**: Foundation ready - all remaining work can assume PostgreSQL-only configuration, bootstrap, and transaction lifecycle.

---

## Phase 3: User Story 1 - Processar faturas com banco único (Priority: P1) 🎯 MVP

**Goal**: Make synchronous and asynchronous invoice processing persist canonical and operational state only through the official PostgreSQL backend.

**Independent Test**: Process a test invoice and resume an interrupted async workflow using only `FATURAMA_DB_DSN`, then verify documents, statements, evidences, transactions, installment plans, projections, summaries, review items, decisions, processing status, and checkpoints are stored in PostgreSQL with no local database files created.

### Tests for User Story 1

- [x] T013 [P] [US1] Rewrite synchronous processing integration coverage for PostgreSQL in `tests/integration/test_langgraph_workflow.py` and `tests/integration/test_review_workflow.py`
- [x] T014 [P] [US1] Rewrite async processing and review-required regression coverage for PostgreSQL in `tests/integration/test_async_dispatch.py` and `tests/integration/test_review_required_status_flow.py`
- [x] T015 [P] [US1] Add checkpoint restore coverage against PostgreSQL in `tests/e2e/test_async_pipeline_regression.py`

### Implementation for User Story 1

- [x] T016 [US1] Refactor canonical repositories to use PostgreSQL-native SQL upserts and remove per-method commits in `src/faturama/infrastructure/repositories/statement_repository.py`, `src/faturama/infrastructure/repositories/transaction_repository.py`, `src/faturama/infrastructure/repositories/installment_repository.py`, `src/faturama/infrastructure/repositories/summary_repository.py`, `src/faturama/infrastructure/repositories/evidence_repository.py`, `src/faturama/infrastructure/repositories/review_repository.py`, and `src/faturama/infrastructure/repositories/decision_repository.py`
- [x] T017 [P] [US1] Refactor async operational repositories to use PostgreSQL-native SQL and boolean semantics in `src/faturama/infrastructure/repositories/processing_job_repository.py`, `src/faturama/infrastructure/repositories/processing_status_repository.py`, and `src/faturama/infrastructure/repositories/artifact_manifest_repository.py`
- [x] T018 [US1] Move `process_invoice` to injected unit-of-work and checkpoint abstractions in `src/faturama/application/use_cases/process_invoice.py`
- [x] T019 [US1] Move async command processing to injected PostgreSQL-only composition in `src/faturama/application/use_cases/process_processing_command.py`
- [x] T020 [US1] Update workflow node wiring to consume repository/checkpoint abstractions instead of SQLite-oriented infrastructure in `src/faturama/application/services/workflow_nodes.py` and `src/faturama/application/services/workflow_builder.py`
- [x] T021 [US1] Add interface composition for invoice processing and worker runtime in `src/faturama/interface/cli/process_invoice.py`, `src/faturama/interface/worker/runner.py`, and new composition modules under `src/faturama/interface/`

**Checkpoint**: User Story 1 should process invoices and async retries entirely through PostgreSQL, with resumable checkpoints and no SQLite code path.

---

## Phase 4: User Story 2 - Consultar dados operacionais pela CLI sem caminhos locais (Priority: P2)

**Goal**: Make all CLI read and review commands use PostgreSQL-backed ports/services rather than `database_path` and raw connections.

**Independent Test**: After processing fixtures into PostgreSQL, execute each CLI read command and review command without any local DB path variables and confirm results are returned from the configured DSN.

### Tests for User Story 2

- [x] T022 [P] [US2] Rewrite CLI contract coverage for DSN-based read commands in `tests/contract/test_cli_queries.py` and `tests/contract/test_cli_process_invoice.py`
- [x] T023 [P] [US2] Rewrite query integration coverage for PostgreSQL-backed read models in `tests/integration/test_monthly_queries.py`, `tests/integration/test_query_performance.py`, and `tests/e2e/test_invoice_pipeline_e2e.py`

### Implementation for User Story 2

- [x] T024 [US2] Replace path-based application queries with injected read ports or query services in `src/faturama/application/queries/list_transactions.py`, `src/faturama/application/queries/list_statements.py`, `src/faturama/application/queries/monthly_spend.py`, `src/faturama/application/queries/current_installments.py`, `src/faturama/application/queries/future_installments.py`, `src/faturama/application/queries/show_statement.py`, and `src/faturama/application/queries/remaining_balance.py`
- [x] T025 [US2] Remove direct connection access from remaining balance and expose explicit repository/query-service methods in `src/faturama/infrastructure/repositories/installment_repository.py` and `src/faturama/application/ports/`
- [x] T026 [US2] Refactor CLI query composition to use PostgreSQL-backed services instead of `_db_path()` in `src/faturama/interface/cli/queries.py` and `src/faturama/interface/cli/composition.py`
- [x] T027 [US2] Refactor review queue and resolve-review commands to use PostgreSQL-backed composition in `src/faturama/interface/cli/review.py`, `src/faturama/interface/cli/composition.py`, and `src/faturama/application/use_cases/review_queue.py`

**Checkpoint**: User Story 2 should provide all operational reads from PostgreSQL through DSN-based composition, independently of the processing entrypoints.

---

## Phase 5: User Story 3 - Operar com contrato de configuração único e confiável (Priority: P3)

**Goal**: Align configuration, tests, local runtime guidance, and documentation around a single PostgreSQL contract.

**Independent Test**: Start the app without `FATURAMA_DB_DSN` and observe explicit failure; then run local CLI/tests against the official compose-backed PostgreSQL environment and confirm docs only describe the PostgreSQL path.

### Tests for User Story 3

- [x] T028 [P] [US3] Replace SQLite-specific fixture coverage with PostgreSQL container-backed fixtures in `tests/conftest.py` and `tests/integration/test_postgres_bootstrap.py`
- [x] T029 [P] [US3] Add configuration failure, DSN rejection, and database-unavailable error coverage in `tests/integration/test_settings.py` and `tests/integration/`

### Implementation for User Story 3

- [x] T030 [US3] Align local runtime and test bootstrap with the official PostgreSQL compose path in `docker-compose.yml`, project helper scripts, and `tests/conftest.py`
- [x] T031 [US3] Update public documentation to describe PostgreSQL as the only supported local and async database in `README.md`, `docs/database-schema.md`, and `docs/runbooks/invoice-processing.md`
- [x] T032 [US3] Update active specs, quickstarts, and repository refinement artifacts that still recommend SQLite in `specs/001-invoice-extractor/`, `specs/003-align-runtime-architecture/`, `specs/004-event-driven-file-processing/`, and relevant refinement files kept with the feature inputs
- [x] T033 [US3] Remove or rewrite SQLite-specific tests and references in `tests/integration/test_sqlite_bootstrap.py`, `tests/unit/`, and any remaining productive-support files flagged by the regression sweep
- [x] T034 [US3] Record the chosen treatment for legacy SQLite data as discard, historical invalidation, or separate migration procedure in `specs/006-postgres-only-persistence/spec.md`, `specs/006-postgres-only-persistence/plan.md`, and implementation-facing docs if needed

**Checkpoint**: User Story 3 should leave the repo with one public runtime contract, one local setup story, and no supported SQLite guidance.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, cleanup, and cross-story acceptance.

- [x] T035 [P] Run the PostgreSQL-only regression sweep and remove remaining banned markers from productive code and scoped documentation in `src/`, `pyproject.toml`, `README.md`, `docs/`, active `specs/`, and maintained refinement artifacts
- [x] T036 [P] Run the full targeted validation suite for processing, CLI reads, checkpoints, configuration failure, and database-unavailable errors under PostgreSQL in `tests/contract/`, `tests/integration/`, and `tests/e2e/`
- [x] T037 Verify end-to-end local execution against `docker-compose.yml` and capture any final documentation corrections in `README.md` and `specs/006-postgres-only-persistence/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and should reuse the composition patterns established in User Story 1
- **User Story 3 (Phase 5)**: Depends on Foundational completion and should be finalized after User Stories 1 and 2 stabilize runtime and CLI behavior
- **Polish (Phase 6)**: Depends on completion of selected user stories

### User Story Dependencies

- **US1 (P1)**: Starts after foundational work and delivers the MVP
- **US2 (P2)**: Depends on the shared PostgreSQL composition and repository surfaces established in US1/Foundational work
- **US3 (P3)**: Depends on finalized configuration/runtime behavior from US1 and US2 so docs and fixtures reflect the real contract

### Within Each User Story

- Tests should be updated before or alongside the implementation they validate.
- Repository and port changes must land before use-case and CLI composition refactors that depend on them.
- Configuration validation must be stable before final documentation and regression sweeps.

## Parallel Execution Examples

### User Story 1

- Run T013, T014, and T015 in parallel once Phase 2 is complete.
- Run T016 and T017 in parallel because they cover different repository groups.

### User Story 2

- Run T022 and T023 in parallel.
- Run T026 and T027 in parallel after T024 and T025 define the read-service contract.

### User Story 3

- Run T028 and T029 in parallel.
- Run T031 and T032 in parallel after T030 stabilizes the official runtime path.
- Run T033 and T034 in parallel after the documentation/refinement scope is settled.

### Polish

- Run T035 and T036 in parallel before T037.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate synchronous processing, async processing, and checkpoint resume against PostgreSQL

### Incremental Delivery

1. Deliver MVP by removing SQLite from processing and async runtime first.
2. Add DSN-only CLI reads and review operations.
3. Finish by aligning tests, compose-based local workflow, and all active documentation.

### Task Count Summary

- **Total tasks**: 37
- **Setup + Foundational**: 12
- **US1**: 9
- **US2**: 6
- **US3**: 7
- **Polish**: 3

### Independent Test Criteria by Story

- **US1**: Processing and async resume persist only in PostgreSQL with no local database files.
- **US2**: All read and review CLI commands return data through the configured PostgreSQL DSN.
- **US3**: Missing or invalid DSN fails fast, indisponibilidade real do banco gera erro operacional claro, e local docs/tests describe only the PostgreSQL path.
