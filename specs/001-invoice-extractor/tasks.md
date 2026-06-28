# Tasks: Extrator de Faturas Estruturadas

**Input**: Design documents from `/specs/001-invoice-extractor/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Testes são obrigatórios nesta feature por exigência explícita do plano e da constituição do projeto.

**Organization**: Tasks agrupadas por user story para permitir implementação incremental, validação independente e entrega de MVP a partir da US1.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependência direta)
- **[Story]**: Mapeia tarefa à user story correspondente (`[US1]`, `[US2]`, `[US3]`)
- Todas as descrições incluem caminhos exatos de arquivo

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criar a estrutura base Python/Clean Architecture, tooling e entrypoints iniciais

- [X] T001 Create package structure under `src/faturama/` and test suite skeleton under `tests/`
- [X] T002 Update `pyproject.toml` with runtime and development dependencies for `opendataloader-pdf[hybrid]`, `pydantic`, `langgraph`, `pytest`, `ruff`, and type checking
- [X] T003 [P] Create package entry modules in `src/faturama/__init__.py` and `src/faturama/interface/cli/__init__.py`
- [X] T004 [P] Configure test discovery and quality tool settings in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Entregar a infraestrutura compartilhada que bloqueia todas as histórias

**⚠️ CRITICAL**: Nenhuma user story deve começar antes do fim desta fase

- [X] T005 Define core domain entities and supporting value objects in `src/faturama/domain/entities/raw_document.py`, `src/faturama/domain/entities/invoice_statement.py`, `src/faturama/domain/entities/transaction_line.py`, `src/faturama/domain/entities/installment_plan.py`, `src/faturama/domain/entities/future_installment_projection.py`, `src/faturama/domain/entities/review_item.py`, `src/faturama/domain/value_objects/money.py`, `src/faturama/domain/value_objects/confidence_score.py`, and `src/faturama/domain/exceptions.py`
- [X] T006 [P] Implement canonical Pydantic DTOs in `src/faturama/application/dto/document_dto.py`, `src/faturama/application/dto/statement_dto.py`, `src/faturama/application/dto/transaction_dto.py`, `src/faturama/application/dto/installment_plan_dto.py`, `src/faturama/application/dto/projection_dto.py`, `src/faturama/application/dto/review_dto.py`, and `src/faturama/application/dto/decision_record_dto.py`
- [X] T007 [P] Define repository and service ports in `src/faturama/application/ports/document_repository.py`, `src/faturama/application/ports/statement_repository.py`, `src/faturama/application/ports/transaction_repository.py`, `src/faturama/application/ports/installment_repository.py`, `src/faturama/application/ports/review_repository.py`, `src/faturama/application/ports/query_service.py`, and `src/faturama/application/ports/extraction_service.py`
- [X] T008 Implement SQLite schema bootstrap and connection management in `src/faturama/infrastructure/database/schema.py` and `src/faturama/infrastructure/database/sqlite.py`
- [X] T009 [P] Implement structured logging and processing metrics helpers in `src/faturama/observability/logging.py` and `src/faturama/observability/metrics.py`
- [X] T010 [P] Implement application configuration and confidence-threshold loading in `src/faturama/infrastructure/config/settings.py`
- [X] T011 Implement OpenDataLoader adapter, raw artifact loader, and issuer/layout strategy registry in `src/faturama/infrastructure/opendataloader/extractor.py`, `src/faturama/infrastructure/files/artifacts.py`, and `src/faturama/infrastructure/opendataloader/issuer_layout_registry.py`
- [X] T012 Implement base LangGraph orchestration state, checkpoint abstraction, and workflow bootstrap in `src/faturama/application/services/workflow_state.py` and `src/faturama/application/services/workflow_builder.py`
- [X] T013 [P] Create foundational integration tests for SQLite bootstrap, config loading, artifact extraction adapters, and issuer-layout registry behavior in `tests/integration/test_sqlite_bootstrap.py`, `tests/integration/test_settings.py`, `tests/integration/test_opendataloader_extractor.py`, and `tests/integration/test_issuer_layout_registry.py`

**Checkpoint**: Estrutura, portas, persistência base e orquestração mínima prontas para iniciar as histórias

---

## Phase 3: User Story 1 - Processar faturas sem perder rastreabilidade (Priority: P1) 🎯 MVP

**Goal**: Processar uma fatura PDF suportada e persistir documento, fatura e lançamentos com evidência auditável

**Independent Test**: Processar uma fatura de exemplo e validar que documento, cabeçalho, transações e evidências foram persistidos sem duplicação no primeiro processamento

### Tests for User Story 1

- [X] T014 [P] [US1] Create contract test for `process-invoice` CLI output in `tests/contract/test_cli_process_invoice.py`
- [X] T015 [P] [US1] Create integration test for first-time invoice ingestion and idempotent document registration in `tests/integration/test_invoice_ingestion.py`
- [X] T016 [P] [US1] Create unit tests for statement header parsing and transaction candidate filtering in `tests/unit/test_header_extraction.py` and `tests/unit/test_transaction_candidate_filter.py`

### Implementation for User Story 1

- [X] T017 [P] [US1] Implement raw document registration and file hash service in `src/faturama/domain/services/document_identity.py`
- [X] T018 [P] [US1] Implement statement repository in `src/faturama/infrastructure/repositories/statement_repository.py`
- [X] T019 [P] [US1] Implement evidence repository in `src/faturama/infrastructure/repositories/evidence_repository.py`
- [X] T020 [P] [US1] Implement deterministic issuer detection service in `src/faturama/domain/services/issuer_detector.py`
- [X] T021 [P] [US1] Implement deterministic header extraction service in `src/faturama/domain/services/header_extractor.py`
- [X] T022 [P] [US1] Implement document section segmentation service in `src/faturama/domain/services/section_segmenter.py`
- [X] T023 [P] [US1] Implement transaction candidate extraction service in `src/faturama/domain/services/transaction_candidate_extractor.py`
- [X] T024 [P] [US1] Implement rule-based transaction line parsing service in `src/faturama/domain/services/transaction_parser.py`
- [X] T025 [US1] Implement the ingestion workflow use case coordinating document load, extraction, parsing, and persistence in `src/faturama/application/use_cases/process_invoice.py`
- [X] T026 [US1] Implement `process-invoice` CLI command in `src/faturama/interface/cli/process_invoice.py`
- [X] T027 [US1] Wire CLI entrypoint dispatch in `src/faturama/cli.py` and replace placeholder logic in `main.py`

**Checkpoint**: A US1 deve permitir ingestão completa e auditável de uma fatura suportada

---

## Phase 4: User Story 2 - Consultar gastos e parcelas por competência e cartão (Priority: P2)

**Goal**: Disponibilizar consultas CLI sobre totais mensais, parcelas cobradas, parcelas futuras e saldo parcelado

**Independent Test**: Com duas faturas consecutivas do mesmo cartão já processadas, consultar gasto mensal e parcelas futuras com respostas consistentes e separação clara entre observado e projetado

### Tests for User Story 2

- [X] T028 [P] [US2] Create contract tests for `monthly-spend`, `current-installments`, `future-installments`, and `remaining-balance` in `tests/contract/test_cli_queries.py`
- [X] T029 [P] [US2] Create integration test for monthly summaries and installment projections in `tests/integration/test_monthly_queries.py`
- [X] T030 [P] [US2] Create unit tests for summary aggregation and future projection rules in `tests/unit/test_monthly_summary.py` and `tests/unit/test_future_projection.py`

### Implementation for User Story 2

- [X] T031 [P] [US2] Implement installment plan matching service with canonical key logic in `src/faturama/domain/services/installment_matcher.py`
- [X] T032 [P] [US2] Implement future projection service in `src/faturama/domain/services/future_projection.py`
- [X] T033 [P] [US2] Implement monthly summary service in `src/faturama/domain/services/monthly_summary.py`
- [X] T034 [P] [US2] Implement installment repository in `src/faturama/infrastructure/repositories/installment_repository.py`
- [X] T035 [P] [US2] Implement summary repository in `src/faturama/infrastructure/repositories/summary_repository.py`
- [X] T036 [US2] Implement statement and transaction query use cases in `src/faturama/application/queries/list_statements.py`, `src/faturama/application/queries/show_statement.py`, and `src/faturama/application/queries/list_transactions.py`
- [X] T037 [US2] Implement monthly and installment query use cases in `src/faturama/application/queries/monthly_spend.py`, `src/faturama/application/queries/current_installments.py`, `src/faturama/application/queries/future_installments.py`, and `src/faturama/application/queries/remaining_balance.py`
- [X] T038 [US2] Implement query CLI commands in `src/faturama/interface/cli/queries.py`
- [X] T039 [US2] Integrate query read models with the ingestion workflow so projections and summaries are refreshed after processing in `src/faturama/application/use_cases/process_invoice.py`

**Checkpoint**: A US2 deve responder consultas analíticas essenciais com base já persistida

---

## Phase 5: User Story 3 - Revisar ambiguidades e reprocessar com segurança (Priority: P3)

**Goal**: Encaminhar automaticamente itens abaixo do limiar para revisão manual, permitir resolução explícita e suportar reprocessamento incremental sem duplicação

**Independent Test**: Processar uma fatura com ambiguidades, abrir fila de revisão, resolver um item e confirmar que o reprocessamento atualiza entidades relacionadas sem duplicar dados

### Tests for User Story 3

- [X] T040 [P] [US3] Create contract test for `review-queue` and `resolve-review` in `tests/contract/test_cli_review.py`
- [X] T041 [P] [US3] Create integration test for low-confidence review flow and incremental reprocessing in `tests/integration/test_review_workflow.py`
- [X] T042 [P] [US3] Create unit tests for confidence policy and decision recording in `tests/unit/test_confidence_policy.py` and `tests/unit/test_decision_recording.py`

### Implementation for User Story 3

- [X] T043 [P] [US3] Implement confidence evaluation and decision-state service in `src/faturama/domain/services/confidence_policy.py`
- [X] T044 [P] [US3] Implement review queue repository in `src/faturama/infrastructure/repositories/review_repository.py`
- [X] T045 [P] [US3] Implement decision record repository in `src/faturama/infrastructure/repositories/decision_repository.py`
- [X] T046 [P] [US3] Implement LLM fallback adapter in `src/faturama/infrastructure/llm/structured_extractor.py`
- [X] T047 [P] [US3] Implement validated ambiguity resolution service in `src/faturama/application/services/ambiguity_resolution.py`
- [X] T048 [US3] Extend the workflow to open review items for all below-threshold entities and checkpoint resumable processing in `src/faturama/application/services/workflow_builder.py`
- [X] T049 [US3] Implement review use cases for listing pending items, applying manual resolution, and re-running affected reconciliation in `src/faturama/application/use_cases/review_queue.py`
- [X] T050 [US3] Implement CLI commands `review-queue` and `resolve-review` in `src/faturama/interface/cli/review.py`
- [X] T051 [US3] Implement idempotent reprocessing reconciliation for transactions, occurrences, and projections in `src/faturama/application/services/reprocessing.py`

**Checkpoint**: A US3 deve fechar o ciclo operacional de baixa confiança, revisão e reprocessamento seguro

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Completar documentação, endurecer qualidade e validar o fluxo inteiro

- [X] T052 [P] Add developer-facing architecture and runbook notes in `README.md` and `docs/runbooks/invoice-processing.md`
- [X] T053 [P] Add remaining domain unit tests for merchant normalization, date parsing, and duplicate detection in `tests/unit/test_merchant_normalization.py`, `tests/unit/test_date_parser.py`, and `tests/unit/test_duplicate_detection.py`
- [X] T054 Add end-to-end regression suite covering US1, US2, and US3 together in `tests/e2e/test_invoice_pipeline_e2e.py`
- [X] T055 Run and document the quickstart validation scenarios in `specs/001-invoice-extractor/quickstart.md`
- [X] T056 Add ingestion and query performance assertions for SC-003 and plan performance goals in `tests/integration/test_processing_performance.py` and `tests/integration/test_query_performance.py`
- [X] T057 Document performance measurement procedure and acceptable thresholds in `docs/runbooks/performance-validation.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: começa imediatamente
- **Phase 2: Foundational**: depende da conclusão da Setup e bloqueia todas as user stories
- **Phase 3: US1**: depende da conclusão da Foundational
- **Phase 4: US2**: depende da conclusão da Foundational e do pipeline base da US1 para gerar dados consultáveis
- **Phase 5: US3**: depende da conclusão da Foundational e se integra ao fluxo de ingestão da US1
- **Phase 6: Polish**: depende das histórias desejadas concluídas

### User Story Dependencies

- **US1 (P1)**: nenhuma dependência de outras histórias; forma o MVP
- **US2 (P2)**: depende de dados processados pela US1, mas permanece testável independentemente depois disso
- **US3 (P3)**: depende do fluxo de ingestão da US1 e complementa a operação sem bloquear o MVP inicial

### Within Each User Story

- Testes vêm antes da implementação principal
- Serviços de domínio antes dos use cases
- Use cases antes dos comandos CLI
- Integração final após repositórios e serviços estarem prontos

### Parallel Opportunities

- Setup: `T003`, `T004`
- Foundational: `T006`, `T007`, `T009`, `T010`, `T013`
- US1: `T014`, `T015`, `T016`, `T017`, `T018`, `T019`, `T020`, `T021`, `T022`, `T023`, `T024`
- US2: `T028`, `T029`, `T030`, `T031`, `T032`, `T033`, `T034`, `T035`
- US3: `T040`, `T041`, `T042`, `T043`, `T044`, `T045`, `T046`, `T047`
- Polish: `T052`, `T053`, `T056`, `T057`

---

## Parallel Example: User Story 1

```bash
# Tests for US1
Task: "T014 [US1] Create contract test for process-invoice in tests/contract/test_cli_process_invoice.py"
Task: "T015 [US1] Create integration test for invoice ingestion in tests/integration/test_invoice_ingestion.py"
Task: "T016 [US1] Create unit tests for header extraction and transaction candidate filtering in tests/unit/"

# Domain and repository work for US1
Task: "T017 [US1] Implement raw document registration in src/faturama/domain/services/document_identity.py"
Task: "T018 [US1] Implement statement repository in src/faturama/infrastructure/repositories/statement_repository.py"
Task: "T019 [US1] Implement evidence repository in src/faturama/infrastructure/repositories/evidence_repository.py"
Task: "T020 [US1] Implement issuer detection service in src/faturama/domain/services/issuer_detector.py"
Task: "T021 [US1] Implement header extraction service in src/faturama/domain/services/header_extractor.py"
Task: "T022 [US1] Implement section segmentation service in src/faturama/domain/services/section_segmenter.py"
Task: "T023 [US1] Implement transaction candidate extraction service in src/faturama/domain/services/transaction_candidate_extractor.py"
Task: "T024 [US1] Implement transaction parser service in src/faturama/domain/services/transaction_parser.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1
4. Validate `process-invoice` end to end against the quickstart scenario
5. Stop and review before opening query and review workflows

### Incremental Delivery

1. Setup + Foundational
2. US1 for ingestion and auditability
3. US2 for analytic queries and projections
4. US3 for manual review and safe reprocessing
5. Polish for documentation and regression hardening

### Parallel Team Strategy

1. Team closes Setup + Foundational together
2. After Foundational:
   - Developer A: US1 pipeline and repositories
   - Developer B: US2 summaries, projections, and query CLI
   - Developer C: US3 confidence policy, review queue, and reprocessing
3. Reunify in Phase 6 for e2e validation

---

## Notes

- Todos os tasks seguem o formato obrigatório com checkbox, ID, marcador `[P]` quando aplicável, label de story e caminho de arquivo
- A implementação deve respeitar as camadas da constituição: domínio sem dependência de infraestrutura, CLI apenas na interface
- A US1 é o escopo sugerido de MVP
