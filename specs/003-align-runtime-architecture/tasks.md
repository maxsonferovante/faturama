# Tasks: Alinhamento de Runtime da Arquitetura

**Input**: Design documents from `/specs/003-align-runtime-architecture/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Testes são obrigatórios nesta feature por constituição do projeto e pelos cenários definidos em `quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar dependências, configuração e fixtures para a troca do runtime.

- [X] T001 Update runtime and dev dependencies for `langgraph-checkpoint-sqlite` and `langchain-opendataloader-pdf` in `pyproject.toml`
- [X] T002 [P] Extend runtime configuration for artifact cache, checkpoint database, OpenDataLoader settings, and agent auto-apply threshold in `src/faturama/infrastructure/config/settings.py`
- [X] T003 [P] Add shared fixtures for runtime artifact directories, checkpoint paths, and OpenDataLoader stubs in `tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura comum que precisa existir antes de qualquer história.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create workflow runtime state models for job status, review cases, and resume metadata in `src/faturama/application/services/workflow_state.py`
- [X] T005 [P] Replace the ad hoc workflow helper with a LangGraph workflow factory and node wiring in `src/faturama/application/services/workflow_builder.py` and `src/faturama/application/services/workflow_nodes.py`
- [X] T006 [P] Add SQLite-backed LangGraph checkpoint integration in `src/faturama/infrastructure/database/langgraph_checkpoint.py`
- [X] T007 [P] Refine extraction service contracts for generated artifacts and runtime reuse in `src/faturama/application/ports/extraction_service.py` and `src/faturama/infrastructure/opendataloader/extractor.py`
- [X] T008 Add workflow observability and structured event logging for extraction, review, resume, and persistence in `src/faturama/observability/logging.py` and `src/faturama/observability/metrics.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Executar o pipeline prometido em runtime (Priority: P1) 🎯 MVP

**Goal**: Fazer `process-invoice` e `process-batch` executarem com `OpenDataLoader` real e orquestração oficial em `LangGraph`.

**Independent Test**: Processar uma fatura suportada sem sidecars pré-gerados e confirmar, via saída do CLI e evidências do job, que a extração primária e a coordenação do fluxo vieram do runtime oficial; quando a extração falhar, o fluxo deve encerrar explicitamente sem fallback legado.

### Tests for User Story 1

- [X] T009 [P] [US1] Add contract coverage for runtime-backed `process-invoice` output in `tests/contract/test_cli_process_invoice.py`
- [X] T010 [P] [US1] Add integration coverage for OpenDataLoader-generated artifacts and explicit no-fallback failure behavior in `tests/integration/test_opendataloader_extractor.py`
- [X] T011 [P] [US1] Add integration coverage for LangGraph workflow execution and checkpoints in `tests/integration/test_langgraph_workflow.py`
- [X] T012 [P] [US1] Add end-to-end coverage for processing a supported invoice without pre-generated sidecars in `tests/e2e/test_invoice_pipeline_e2e.py`

### Implementation for User Story 1

- [X] T013 [P] [US1] Implement OpenDataLoader runtime extraction, artifact generation, and reuse policy in `src/faturama/infrastructure/opendataloader/extractor.py`
- [X] T014 [P] [US1] Update artifact helpers to treat Markdown/JSON as runtime-generated cache and remove legacy fallback resolution from `src/faturama/infrastructure/files/artifacts.py`
- [X] T015 [US1] Implement the canonical LangGraph nodes for `extract_document`, `parse_statement`, `classify_transactions`, `persist_canonical_data`, and `finalize_job` in `src/faturama/application/services/workflow_nodes.py`
- [X] T016 [US1] Refactor invoice ingestion to execute through the compiled LangGraph workflow and fail explicitly on insufficient primary extraction in `src/faturama/application/use_cases/process_invoice.py`
- [X] T017 [US1] Preserve CLI behavior while wiring batch execution to the official runtime workflow in `src/faturama/interface/cli/process_invoice.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Preservar interpretação assistida e revisão sem rotas paralelas (Priority: P2)

**Goal**: Integrar ambiguidade, autoaplicação do agente com limiar alto, pausa por revisão e retomada ao mesmo workflow oficial.

**Independent Test**: Processar uma fatura ambígua e confirmar que casos elegíveis são autoaplicados pelo agente com trilha auditável, enquanto os demais entram em revisão e retomada sem sair do caminho oficial.

### Tests for User Story 2

- [X] T018 [P] [US2] Add unit coverage for ambiguity routing, auto-apply threshold, and review state transitions in `tests/unit/test_ambiguity_resolution.py`
- [X] T019 [P] [US2] Add integration coverage for auto-applied decisions, interrupt, checkpoint restore, and resume flow in `tests/integration/test_review_workflow.py`
- [X] T020 [P] [US2] Add contract coverage for `review-queue` and `resolve-review` after workflow-managed pauses in `tests/contract/test_cli_review.py`

### Implementation for User Story 2

- [X] T021 [P] [US2] Implement LangChain-based review context loading with `OpenDataLoaderPDFLoader` in `src/faturama/infrastructure/llm/review_context_loader.py`
- [X] T022 [P] [US2] Replace the ambiguity placeholder with agent-assisted review orchestration and audit payload generation in `src/faturama/application/services/ambiguity_resolution.py` and `src/faturama/infrastructure/llm/structured_extractor.py`
- [X] T023 [US2] Add the `resolve_ambiguities` LangGraph branch with auto-apply threshold gating and interrupt/resume semantics in `src/faturama/application/services/workflow_nodes.py` and `src/faturama/application/services/workflow_builder.py`
- [X] T024 [US2] Extend review queue resolution to reconcile workflow resume data and checkpoint continuation in `src/faturama/application/use_cases/review_queue.py` and `src/faturama/infrastructure/repositories/review_repository.py`
- [X] T025 [US2] Persist audit evidence for every auto-applied agent decision in `src/faturama/infrastructure/repositories/decision_repository.py` and `src/faturama/application/use_cases/process_invoice.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Reprocessar e consultar sem regressão funcional (Priority: P3)

**Goal**: Garantir idempotência, continuidade das consultas válidas, invalidação do histórico legado e fechamento do desvio arquitetural detectado pela feature `002`.

**Independent Test**: Reprocessar o mesmo documento no fluxo oficial corrigido, bloquear consultas sobre histórico legado inválido, consultar apenas dados reconstruídos válidos e validar por evidências de execução e testes que `LangGraph` e `OpenDataLoader` estão integrados ao runtime real.

### Tests for User Story 3

- [X] T026 [P] [US3] Add integration coverage for idempotent reprocessing with workflow-generated artifacts and partial persistence markers in `tests/integration/test_invoice_ingestion.py`
- [X] T027 [P] [US3] Add contract coverage for blocking query access to invalidated legacy history in `tests/contract/test_cli_queries.py`
- [X] T028 [P] [US3] Add integration coverage for runtime-aligned workflow evidence in `tests/integration/test_langgraph_workflow.py` and `tests/integration/test_opendataloader_extractor.py`
- [X] T029 [P] [US3] Add end-to-end regression coverage for reprocess + legacy invalidation + remaining valid queries in `tests/e2e/test_invoice_pipeline_e2e.py`

### Implementation for User Story 3

- [X] T030 [P] [US3] Update ingestion persistence flow to keep reprocessing idempotent with workflow checkpoints, generated artifacts, and explicit partial markers in `src/faturama/application/use_cases/process_invoice.py`
- [X] T031 [P] [US3] Preserve query semantics and observed-vs-projected separation while rejecting invalidated legacy history in `src/faturama/application/queries/monthly_spend.py`, `src/faturama/application/queries/future_installments.py`, `src/faturama/application/queries/remaining_balance.py`, and `src/faturama/application/queries/list_statements.py`
- [X] T032 [P] [US3] Implement legacy-history invalidation and manual rebuild gating in `src/faturama/infrastructure/repositories/statement_repository.py`, `src/faturama/infrastructure/repositories/summary_repository.py`, and `src/faturama/infrastructure/database/schema.py`
- [X] T033 [US3] Confirm runtime alignment through workflow, extraction, and persistence behavior in `src/faturama/application/services/workflow_nodes.py`, `src/faturama/infrastructure/opendataloader/extractor.py`, and `src/faturama/application/use_cases/process_invoice.py`
- [X] T034 [US3] Align runtime artifact persistence and document identity handling with regenerated Markdown/JSON outputs and invalid legacy status in `src/faturama/domain/entities/raw_document.py` and `src/faturama/domain/services/document_identity.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Fechamentos transversais, documentação e validação final.

- [X] T035 [P] Update operator and architecture documentation for the official runtime flow, auto-apply policy, and legacy invalidation policy in `README.md` and `docs/`
- [X] T036 Add regression notes and troubleshooting guidance for OpenDataLoader/Java/hybrid mode, partial persistence, and manual legacy reconstruction in `specs/003-align-runtime-architecture/quickstart.md`
- [X] T037 Run the full validation matrix from `specs/003-align-runtime-architecture/quickstart.md` and capture any required adjustments in `specs/003-align-runtime-architecture/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and benefits from User Story 1 runtime nodes being present
- **User Story 3 (Phase 5)**: Depends on User Story 1 runtime execution and User Story 2 review/resume flow
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - establishes the official runtime MVP
- **User Story 2 (P2)**: Depends on the official workflow from US1 and adds auto-apply/review-resume behavior
- **User Story 3 (P3)**: Depends on the official workflow from US1 and on the review-aware persistence from US2

### Within Each User Story

- Tests should be written before implementation and fail against the current behavior
- Runtime adapters and models before workflow orchestration
- Workflow orchestration before CLI glue and end-to-end validation
- Story complete before moving to the next dependent story

### Parallel Opportunities

- `T002` and `T003` can run in parallel
- `T005`, `T006`, and `T007` can run in parallel after `T004`
- All US1 test tasks (`T009`-`T012`) can run in parallel
- `T013` and `T014` can run in parallel before `T015`
- All US2 test tasks (`T018`-`T020`) can run in parallel
- `T021` and `T022` can run in parallel before `T023`
- All US3 test tasks (`T026`-`T029`) can run in parallel
- `T030`, `T031`, `T032`, and `T034` can run in parallel before `T033`

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests together:
Task: "Add contract coverage for runtime-backed process-invoice output in tests/contract/test_cli_process_invoice.py"
Task: "Add integration coverage for OpenDataLoader-generated artifacts in tests/integration/test_opendataloader_extractor.py"
Task: "Add integration coverage for LangGraph workflow execution and checkpoints in tests/integration/test_langgraph_workflow.py"

# Launch US1 implementation tasks that touch different files:
Task: "Implement OpenDataLoader runtime extraction, artifact generation, and reuse policy in src/faturama/infrastructure/opendataloader/extractor.py"
Task: "Update artifact helpers to treat Markdown/JSON as runtime-generated cache instead of required external inputs in src/faturama/infrastructure/files/artifacts.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch US2 tests together:
Task: "Add unit coverage for ambiguity routing and review state transitions in tests/unit/test_ambiguity_resolution.py"
Task: "Add integration coverage for interrupt, checkpoint restore, and resume flow in tests/integration/test_review_workflow.py"
Task: "Add contract coverage for review-queue and resolve-review after workflow-managed pauses in tests/contract/test_cli_review.py"

# Launch US2 context/adaptor work together:
Task: "Implement LangChain-based review context loading with OpenDataLoaderPDFLoader in src/faturama/infrastructure/llm/review_context_loader.py"
Task: "Replace the ambiguity placeholder with agent-assisted review orchestration in src/faturama/application/services/ambiguity_resolution.py and src/faturama/infrastructure/llm/structured_extractor.py"
```

---

## Parallel Example: User Story 3

```bash
# Launch US3 regression tests together:
Task: "Add integration coverage for idempotent reprocessing with workflow-generated artifacts and partial persistence markers in tests/integration/test_invoice_ingestion.py"
Task: "Add contract coverage for blocking query access to invalidated legacy history in tests/contract/test_cli_queries.py"
Task: "Add integration coverage for runtime-aligned workflow evidence in tests/integration/test_langgraph_workflow.py and tests/integration/test_opendataloader_extractor.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE** with `process-invoice` and the US1 tests
5. Use workflow execution, extraction artifacts, and persistence checks as a first architectural sanity check

### Incremental Delivery

1. Deliver the official runtime flow in US1
2. Add auto-apply/review-resume orchestration in US2
3. Close idempotency, partial persistence, legacy invalidation, and query regressions in US3
4. Finish with documentation and full quickstart validation in Phase 6

### Parallel Team Strategy

1. One developer handles dependency/config setup while another prepares fixtures
2. After Foundation:
   - Developer A: US1 runtime extraction and workflow
   - Developer B: US2 auto-apply/review branch and agent context loading
   - Developer C: US3 regressions in queries and legacy invalidation after US1 estabilizar
