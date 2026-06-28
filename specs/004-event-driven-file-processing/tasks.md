---

description: "Task list for event-driven asynchronous invoice processing"

---

# Tasks: Processamento Assincrono de Faturas por Eventos

**Input**: Design documents from `/specs/004-event-driven-file-processing/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Testes de contrato, integração e e2e são obrigatórios nesta feature porque a especificação, o quickstart e a constituição exigem validação automatizada do novo fluxo assíncrono.

**Organization**: Tasks grouped by user story to preserve independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criar a base estrutural do runtime assíncrono e do ambiente local.

- [X] T001 Create async runtime package skeleton in `src/faturama/interface/worker/__init__.py`, `src/faturama/infrastructure/aws/__init__.py`, and `src/faturama/infrastructure/messaging/__init__.py`
- [X] T002 Create local worker container bootstrap in `docker/worker/Dockerfile` and `docker-compose.yml`
- [X] T003 [P] Create Terraform skeleton for shared module and environments in `infra/terraform/modules/faturama_runtime/main.tf`, `infra/terraform/environments/local/main.tf`, and `infra/terraform/environments/aws/main.tf`
- [X] T004 [P] Extend packaging and developer commands for the async runtime in `pyproject.toml` and `README.md`
- [X] T005 [P] Create async test fixtures and sample payload assets in `tests/contract/fixtures/processing_message.json`, `tests/integration/fixtures/s3_event.json`, and `tests/e2e/fixtures/invoice-2026-04.pdf`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Entregar os contratos internos, persistência operacional e configuração comum que bloqueiam todas as histórias.

**⚠️ CRITICAL**: No user story work should start before this phase is complete.

- [X] T006 Extend async runtime settings and environment parsing in `src/faturama/infrastructure/config/settings.py`
- [X] T007 [P] Add PostgreSQL-capable schema bootstrap and connection adapter for operational tables in `src/faturama/infrastructure/database/schema.py` and `src/faturama/infrastructure/database/postgres.py`
- [X] T008 [P] Define async DTOs and value objects for processing commands, status, grants, and manifests in `src/faturama/application/dto/processing_command_dto.py`, `src/faturama/application/dto/processing_status_dto.py`, and `src/faturama/domain/value_objects/processing_status.py`
- [X] T009 [P] Define application ports for object storage, processing ledger, status projection, and artifact manifests in `src/faturama/application/ports/object_storage.py`, `src/faturama/application/ports/processing_job_repository.py`, `src/faturama/application/ports/processing_status_repository.py`, and `src/faturama/application/ports/artifact_manifest_repository.py`
- [X] T010 Implement SQL repositories for processing jobs, status read model, artifact manifests, and upload grants in `src/faturama/infrastructure/repositories/processing_job_repository.py`, `src/faturama/infrastructure/repositories/processing_status_repository.py`, `src/faturama/infrastructure/repositories/artifact_manifest_repository.py`, and `src/faturama/infrastructure/repositories/upload_grant_repository.py`
- [X] T011 [P] Add `processing_id` correlation logging and metrics helpers in `src/faturama/observability/logging.py` and `src/faturama/observability/metrics.py`
- [X] T012 Create Terraform variables and outputs shared by local and AWS runtimes in `infra/terraform/modules/faturama_runtime/variables.tf`, `infra/terraform/modules/faturama_runtime/outputs.tf`, `infra/terraform/environments/local/variables.tf`, and `infra/terraform/environments/aws/variables.tf`

**Checkpoint**: Foundation ready for independent story work.

---

## Phase 3: User Story 1 - Submeter arquivos sem bloqueio (Priority: P1) 🎯 MVP

**Goal**: Permitir upload autorizado, dispatch assíncrono e início rastreável do processamento sem bloquear o solicitante.

**Independent Test**: Enviar um PDF elegível pelo fluxo local, confirmar geração de `processing_id`, registro inicial de status e dispatch do worker sem esperar o resultado final.

### Tests for User Story 1

- [X] T013 [P] [US1] Add contract tests for signed upload grants and processing message payloads in `tests/contract/test_signed_upload_contract.py` and `tests/contract/test_processing_message_contract.py`
- [X] T014 [P] [US1] Add integration test for S3 event normalization and initial ledger creation in `tests/integration/test_async_dispatch.py`
- [X] T015 [P] [US1] Add e2e test for `upload -> queue -> state machine -> ecs dispatch` in `tests/e2e/test_event_driven_dispatch_e2e.py`

### Implementation for User Story 1

- [X] T016 [P] [US1] Implement source-event normalization and processing command builder with dedupe keys for duplicate/out-of-order deliveries in `src/faturama/application/services/source_event_normalizer.py` and `src/faturama/application/use_cases/build_processing_command.py`
- [X] T017 [P] [US1] Implement worker entrypoint and command runner that delegate to `process_invoice` in `src/faturama/interface/worker/entrypoint.py` and `src/faturama/interface/worker/runner.py`
- [X] T018 [P] [US1] Implement S3 object download/upload adapters and signed-upload grant correlation in `src/faturama/infrastructure/aws/s3_storage.py` and `src/faturama/infrastructure/repositories/upload_grant_repository.py`
- [X] T019 [US1] Implement async dispatch orchestration that records `PENDING` and `RUNNING` and ignores duplicate or stale source deliveries per idempotency policy in `src/faturama/application/use_cases/process_processing_command.py`
- [X] T020 [US1] Provision input bucket, SQS, DLQ, EventBridge Pipe, Step Function, and ECS task wiring sized for the v1 burst target in `infra/terraform/modules/faturama_runtime/main.tf`, `infra/terraform/environments/local/main.tf`, and `infra/terraform/environments/aws/main.tf`

**Checkpoint**: User Story 1 is functional when asynchronous submission and initial tracking work without a synchronous CLI dependency.

---

## Phase 4: User Story 2 - Operar o fluxo por eventos com revisão controlada (Priority: P2)

**Goal**: Registrar o ciclo de vida do processamento, manter `REVIEW_REQUIRED` como estado pendente e permitir retomada rastreável.

**Independent Test**: Processar um documento ambíguo, validar transições persistidas até `REVIEW_REQUIRED` e comprovar retomada posterior sem reiniciar a solicitação.

### Tests for User Story 2

- [X] T021 [P] [US2] Add contract and integration tests for status read model transitions and `REVIEW_REQUIRED` semantics in `tests/contract/test_processing_status_read_model.py` and `tests/integration/test_review_required_status_flow.py`
- [X] T022 [P] [US2] Add integration test for checkpoint restore and review resume in `tests/integration/test_async_review_resume.py`

### Implementation for User Story 2

- [X] T023 [P] [US2] Implement lifecycle transition service and status projection updater in `src/faturama/application/services/processing_lifecycle.py` and `src/faturama/application/use_cases/update_processing_status.py`
- [X] T024 [P] [US2] Implement PostgreSQL-backed checkpoint runtime for resumable async execution in `src/faturama/infrastructure/database/postgres_checkpoint.py` and `src/faturama/infrastructure/database/langgraph_checkpoint.py`
- [X] T025 [P] [US2] Extend review workflow nodes to keep `REVIEW_REQUIRED` non-terminal and reopenable in `src/faturama/application/services/workflow_nodes.py`, `src/faturama/application/services/workflow_state.py`, and `src/faturama/application/services/reprocessing.py`
- [X] T026 [P] [US2] Persist lifecycle events and status read-model updates from worker execution in `src/faturama/infrastructure/repositories/processing_job_repository.py` and `src/faturama/infrastructure/repositories/processing_status_repository.py`
- [X] T027 [US2] Configure dispatch failure handling, retries, observability metadata, and lifecycle-event persistence semantics in `infra/terraform/modules/faturama_runtime/main.tf` and `src/faturama/interface/worker/runner.py`

**Checkpoint**: User Story 2 is functional when operators can inspect status transitions, see `REVIEW_REQUIRED` as non-terminal, and resume execution safely.

---

## Phase 5: User Story 3 - Consumir resultados sem regressao funcional (Priority: P3)

**Goal**: Preservar os resultados canônicos da pipeline atual com idempotência, manifesto de artefatos e referências consultáveis de resultado.

**Independent Test**: Reprocessar documentos conhecidos e confirmar ausência de duplicação canônica, persistência dos artefatos em `processados-faturama` e status finais coerentes com o resultado produzido.

### Tests for User Story 3

- [X] T028 [P] [US3] Add regression tests for idempotent reprocessing, artifact manifest persistence, and partial outcomes in `tests/unit/test_processing_idempotency.py`, `tests/integration/test_artifact_manifest_persistence.py`, and `tests/e2e/test_async_pipeline_regression.py`

### Implementation for User Story 3

- [X] T029 [P] [US3] Implement deterministic artifact key builder and manifest persistence services in `src/faturama/application/services/artifact_key_builder.py` and `src/faturama/application/services/artifact_manifest_service.py`
- [X] T030 [P] [US3] Implement artifact manifest repository and S3 artifact writer for `processados-faturama` in `src/faturama/infrastructure/repositories/artifact_manifest_repository.py` and `src/faturama/infrastructure/aws/s3_storage.py`
- [X] T031 [P] [US3] Adapt canonical persistence to reuse document hash and avoid duplicate records across retries in `src/faturama/application/use_cases/process_invoice.py`, `src/faturama/domain/services/document_identity.py`, and `src/faturama/infrastructure/repositories/statement_repository.py`
- [X] T032 [P] [US3] Persist `SUCCESS`, `PARTIAL`, and `FAILED` result references plus artifact links for the status API in `src/faturama/application/use_cases/process_processing_command.py` and `src/faturama/application/services/processing_status_service.py`
- [X] T033 [US3] Implement retry-safe processing ledger rules for repeated PDFs and new `processing_id` attempts in `src/faturama/infrastructure/repositories/processing_job_repository.py` and `src/faturama/application/services/reprocessing.py`
- [X] T034 [US3] Wire artifact bucket segregation and retry-safe runtime config across infra and app in `infra/terraform/modules/faturama_runtime/main.tf`, `infra/terraform/environments/local/main.tf`, and `src/faturama/infrastructure/config/settings.py`

**Checkpoint**: User Story 3 is functional when the async flow preserves the canonical business output and exposes stable references for consumers.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Consolidar validação local, documentação operacional e paridade entre ambientes.

- [X] T035 [P] Update local validation guide and parity caveats for lifecycle events, SLA targets, and concurrency expectations in `README.md`, `specs/004-event-driven-file-processing/quickstart.md`, and `specs/004-event-driven-file-processing/contracts/runtime-config.md`
- [X] T036 [P] Add automated latency verification for `5 minutos` completion and `30 segundos` status propagation in `tests/integration/test_status_propagation_latency.py` and `tests/e2e/test_async_sla.py`
- [X] T037 [P] Add concurrent burst and failure-isolation validation for 20 eligible uploads in `tests/e2e/test_async_concurrency_burst.py` and `tests/integration/test_worker_failure_isolation.py`
- [X] T038 [P] Add duplicate, delayed, and out-of-order source-event validation in `tests/integration/test_source_event_deduplication.py` and `tests/integration/test_source_event_ordering.py`
- [X] T039 [P] Add automated local infra/runtime verification for the async contract in `tests/e2e/test_local_runtime_contract.py` and `infra/terraform/environments/local/outputs.tf`
- [X] T040 [P] Document operational runbook and operator-diagnosis checklist for dispatch, review resume, and failure triage in `docs/runbooks/event-driven-file-processing.md` and `tests/e2e/test_operational_diagnostics.py`
- [X] T041 Run repository quality gates and record the async verification command matrix in `README.md` and `docs/runbooks/event-driven-file-processing.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies and should start immediately.
- Foundational (Phase 2) depends on Setup and blocks all story work.
- User Story 1 (Phase 3) depends on Foundational and is the MVP cut.
- User Story 2 (Phase 4) depends on User Story 1 because it extends the dispatched worker lifecycle and persisted status model.
- User Story 3 (Phase 5) depends on User Story 1 for async execution and on User Story 2 for stable status/review semantics.
- Polish (Phase 6) depends on the stories selected for delivery.

### User Story Dependencies

- US1 depends only on the foundational phase.
- US2 depends on the async dispatch and worker wiring delivered by US1.
- US3 depends on the async runtime from US1 and the persisted lifecycle semantics from US2.

### Within Each User Story

- Tests must be implemented before the corresponding production changes and should fail first.
- DTOs and ports should land before adapters and use cases.
- Infrastructure wiring should follow working application code, not precede it.
- Each story should end with its own independent validation before moving forward.

### Parallel Opportunities

- T003, T004, and T005 can run in parallel after T001/T002 define the base structure.
- T007, T008, T009, T011, and T012 can run in parallel during the foundational phase.
- In US1, T013, T014, and T015 can run together, then T016, T017, and T018 can run in parallel before T019/T020.
- In US2, T021 and T022 can run together, then T023, T024, T025, and T026 can run in parallel before T027.
- In US3, T028 can start first, then T029, T030, T031, and T032 can run in parallel before T033/T034.
- T035, T036, T037, T038, T039, and T040 can run in parallel once the targeted stories are complete.

---

## Parallel Example: User Story 1

```bash
Task: "T013 Add contract tests for signed upload grants and processing message payloads in tests/contract/test_signed_upload_contract.py and tests/contract/test_processing_message_contract.py"
Task: "T014 Add integration test for S3 event normalization and initial ledger creation in tests/integration/test_async_dispatch.py"
Task: "T015 Add e2e test for upload -> queue -> state machine -> ecs dispatch in tests/e2e/test_event_driven_dispatch_e2e.py"

Task: "T016 Implement source-event normalization and processing command builder in src/faturama/application/services/source_event_normalizer.py and src/faturama/application/use_cases/build_processing_command.py"
Task: "T017 Implement worker entrypoint and command runner that delegate to process_invoice in src/faturama/interface/worker/entrypoint.py and src/faturama/interface/worker/runner.py"
Task: "T018 Implement S3 object download/upload adapters and signed-upload grant correlation in src/faturama/infrastructure/aws/s3_storage.py and src/faturama/infrastructure/repositories/upload_grant_repository.py"
```

---

## Parallel Example: User Story 2

```bash
Task: "T021 Add contract and integration tests for status read model transitions and REVIEW_REQUIRED semantics in tests/contract/test_processing_status_read_model.py and tests/integration/test_review_required_status_flow.py"
Task: "T022 Add integration test for checkpoint restore and review resume in tests/integration/test_async_review_resume.py"

Task: "T023 Implement lifecycle transition service and status projection updater in src/faturama/application/services/processing_lifecycle.py and src/faturama/application/use_cases/update_processing_status.py"
Task: "T024 Implement PostgreSQL-backed checkpoint runtime for resumable async execution in src/faturama/infrastructure/database/postgres_checkpoint.py and src/faturama/infrastructure/database/langgraph_checkpoint.py"
Task: "T025 Extend review workflow nodes to keep REVIEW_REQUIRED non-terminal and reopenable in src/faturama/application/services/workflow_nodes.py, src/faturama/application/services/workflow_state.py, and src/faturama/application/services/reprocessing.py"
Task: "T026 Persist lifecycle events and status read-model updates from worker execution in src/faturama/infrastructure/repositories/processing_job_repository.py and src/faturama/infrastructure/repositories/processing_status_repository.py"
```

---

## Parallel Example: User Story 3

```bash
Task: "T028 Add regression tests for idempotent reprocessing, artifact manifest persistence, and partial outcomes in tests/unit/test_processing_idempotency.py, tests/integration/test_artifact_manifest_persistence.py, and tests/e2e/test_async_pipeline_regression.py"

Task: "T029 Implement deterministic artifact key builder and manifest persistence services in src/faturama/application/services/artifact_key_builder.py and src/faturama/application/services/artifact_manifest_service.py"
Task: "T030 Implement artifact manifest repository and S3 artifact writer for processados-faturama in src/faturama/infrastructure/repositories/artifact_manifest_repository.py and src/faturama/infrastructure/aws/s3_storage.py"
Task: "T031 Adapt canonical persistence to reuse document hash and avoid duplicate records across retries in src/faturama/application/use_cases/process_invoice.py, src/faturama/domain/services/document_identity.py, and src/faturama/infrastructure/repositories/statement_repository.py"
Task: "T032 Persist SUCCESS, PARTIAL, and FAILED result references plus artifact links for the status API in src/faturama/application/use_cases/process_processing_command.py and src/faturama/application/services/processing_status_service.py"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate asynchronous submission end-to-end before continuing.

### Incremental Delivery

1. Deliver US1 to replace the synchronous entry path with an event-driven dispatch.
2. Deliver US2 to make the lifecycle observable and review-safe.
3. Deliver US3 to recover full business fidelity, idempotence, and consumer-facing result references.
4. Finish with Phase 6 documentation and local verification automation.

### Parallel Team Strategy

1. One engineer can own Terraform and local runtime setup while another prepares async DTOs, ports, and repositories during Phases 1 and 2.
2. After Foundational, one engineer can take worker/dispatch code while another builds contract and integration coverage for US1.
3. Once US1 is stable, US2 lifecycle work and US3 canonical persistence work can progress in parallel with careful coordination on shared repositories.

---

## Notes

- `[P]` marks tasks that can proceed without waiting on another incomplete task in the same phase.
- `[US1]`, `[US2]`, and `[US3]` map directly to the priority-ordered user stories in `spec.md`.
- Every task above includes at least one exact file path so an implementation agent can act without rediscovering scope.
- Suggested MVP scope: complete through T020, then validate before opening US2 or US3.
