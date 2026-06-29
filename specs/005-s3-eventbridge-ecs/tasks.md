---

description: "Task list for S3 -> EventBridge -> ECS runtime redesign"

---

# Tasks: S3 EventBridge ECS

**Input**: Design documents from `/specs/005-s3-eventbridge-ecs/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Testes de contrato, integração e e2e são obrigatórios nesta feature porque a especificação e o quickstart exigem prova ponta a ponta do fluxo real sem invocação local do worker.

**Organization**: Tasks grouped by user story to preserve independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar a superfície de arquivos que precisa ser atualizada para remover o fluxo legado e introduzir o dispatch direto.

- [X] T001 Atualizar o plano operacional da feature em `specs/005-s3-eventbridge-ecs/quickstart.md` e `README.md` para refletir `S3 -> EventBridge -> ECS`
- [X] T002 [P] Preparar a superfície Terraform alvo em `infra/terraform/modules/faturama_runtime/main.tf`, `infra/terraform/modules/faturama_runtime/variables.tf`, and `infra/terraform/modules/faturama_runtime/outputs.tf`
- [X] T003 [P] Preparar os ambientes Terraform em `infra/terraform/environments/local/main.tf`, `infra/terraform/environments/local/variables.tf`, `infra/terraform/environments/local/outputs.tf`, `infra/terraform/environments/aws/main.tf`, and `infra/terraform/environments/aws/variables.tf`
- [X] T004 [P] Preparar os scripts operacionais em `scripts/bootstrap_local_runtime.sh` and `scripts/test_worker_from_ministack_s3.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Remover os contratos e parâmetros compartilhados do fluxo legado antes de entrar nas histórias.

**⚠️ CRITICAL**: No user story work should start before this phase is complete.

- [X] T005 Remover recursos intermediários e locals legados de SQS, Lambda e Step Functions em `infra/terraform/modules/faturama_runtime/main.tf`
- [X] T006 [P] Remover variáveis e outputs legados de fila, pipe e state machine em `infra/terraform/modules/faturama_runtime/variables.tf`, `infra/terraform/modules/faturama_runtime/outputs.tf`, `infra/terraform/environments/local/variables.tf`, `infra/terraform/environments/local/outputs.tf`, and `infra/terraform/environments/aws/variables.tf`
- [X] T007 [P] Alinhar inputs dos ambientes local e AWS ao contrato novo em `infra/terraform/environments/local/main.tf` and `infra/terraform/environments/aws/main.tf`
- [X] T008 [P] Atualizar o contrato de parsing do worker para a origem `aws.s3.eventbridge` em `src/faturama/application/services/source_event_normalizer.py`, `src/faturama/application/dto/processing_command_dto.py`, and `src/faturama/interface/worker/entrypoint.py`
- [X] T009 [P] Atualizar fixtures e testes de contrato do payload de processamento em `tests/contract/fixtures/processing_message.json` and `tests/contract/test_processing_message_contract.py`

**Checkpoint**: Foundation ready for story work.

---

## Phase 3: User Story 1 - Disparar processamento direto por upload (Priority: P1) 🎯 MVP

**Goal**: Fazer um upload elegível no bucket de entrada disparar uma execução real do worker diretamente pelo EventBridge.

**Independent Test**: Enviar um PDF para o bucket de entrada e observar criação de task/container real do worker e artefatos no bucket de saída, sem `run_processing_message` local, sem SQS e sem Step Functions.

### Tests for User Story 1

- [X] T010 [P] [US1] Atualizar o teste e2e do dispatch para o caminho direto em `tests/e2e/test_event_driven_dispatch_e2e.py`
- [X] T011 [P] [US1] Atualizar o script de teste assíncrono real para observar EventBridge -> ECS em `scripts/test_worker_from_ministack_s3.py`
- [X] T012 [P] [US1] Atualizar a validação de contrato local do runtime em `tests/e2e/test_local_runtime_contract.py`

### Implementation for User Story 1

- [X] T013 [P] [US1] Criar a regra EventBridge do bucket de entrada com filtro preciso de chave em `infra/terraform/modules/faturama_runtime/main.tf`
- [X] T014 [P] [US1] Criar a role e o target EventBridge -> ECS RunTask com override do container `worker` em `infra/terraform/modules/faturama_runtime/main.tf`
- [X] T015 [US1] Montar o `FATURAMA_PROCESSING_MESSAGE` a partir do evento S3 do EventBridge em `infra/terraform/modules/faturama_runtime/main.tf`
- [X] T016 [US1] Ajustar a normalização do comando para derivar `processing_id` do envelope EventBridge e aceitar os novos metadados em `src/faturama/application/services/source_event_normalizer.py`
- [X] T017 [US1] Atualizar o bootstrap local para aplicar e validar o runtime direto em `scripts/bootstrap_local_runtime.sh`

**Checkpoint**: User Story 1 is complete when direct upload dispatch works end-to-end without the legacy intermediaries.

---

## Phase 4: User Story 2 - Simplificar a operação da infraestrutura (Priority: P2)

**Goal**: Deixar a infraestrutura local e AWS mínima, previsível e coerente com o novo contrato.

**Independent Test**: Provisionar o ambiente do zero e confirmar, via outputs e validação Terraform, que restam apenas buckets, EventBridge, ECS e IAM necessários ao fluxo.

### Tests for User Story 2

- [X] T018 [P] [US2] Atualizar a validação Terraform do ambiente local em `tests/e2e/test_local_runtime_contract.py` and `infra/terraform/environments/local/outputs.tf`
- [X] T019 [P] [US2] Atualizar a checagem de provisionamento mínimo no quickstart em `specs/005-s3-eventbridge-ecs/quickstart.md`

### Implementation for User Story 2

- [X] T020 [P] [US2] Remover provider endpoints e dependências não usadas do ambiente local em `infra/terraform/environments/local/main.tf`
- [X] T021 [P] [US2] Remover provider `archive` e referências de artefato Lambda dos ambientes Terraform em `infra/terraform/environments/local/main.tf` and `infra/terraform/environments/aws/main.tf`
- [X] T022 [US2] Atualizar outputs e nomes expostos do runtime para o novo desenho em `infra/terraform/modules/faturama_runtime/outputs.tf` and `infra/terraform/environments/local/outputs.tf`
- [X] T023 [US2] Atualizar a documentação operacional do bootstrap e da arquitetura ativa em `README.md` and `specs/005-s3-eventbridge-ecs/contracts/runtime-config.md`

**Checkpoint**: User Story 2 is complete when the runtime can be provisioned and understood sem superfícies legadas no caminho principal.

---

## Phase 5: User Story 3 - Preservar rastreabilidade e resultado do processamento (Priority: P3)

**Goal**: Manter correlação auditável entre upload, tentativa e artefatos mesmo com a simplificação do dispatch.

**Independent Test**: Processar um PDF conhecido e confirmar que o worker publica artefatos em `processados-faturama` com correlação rastreável ao evento e à tentativa real iniciada pelo EventBridge.

### Tests for User Story 3

- [X] T024 [P] [US3] Atualizar os testes de regressão do pipeline assíncrono para remover dependência de Step Functions em `tests/e2e/test_async_pipeline_regression.py`
- [X] T025 [P] [US3] Atualizar os testes de persistência e status para a nova origem do comando em `tests/integration/test_artifact_manifest_persistence.py`, `tests/integration/test_status_propagation_latency.py`, and `tests/integration/test_worker_failure_isolation.py`

### Implementation for User Story 3

- [X] T026 [P] [US3] Persistir metadados de origem EventBridge na criação do job e do status em `src/faturama/application/use_cases/process_processing_command.py` and `src/faturama/infrastructure/repositories/processing_job_repository.py`
- [X] T027 [P] [US3] Atualizar a escrita do manifesto e a correlação dos artefatos com a tentativa real em `src/faturama/application/services/artifact_manifest_service.py` and `src/faturama/application/services/artifact_key_builder.py`
- [X] T028 [US3] Atualizar a observabilidade do runner para expor evidência operacional suficiente do dispatch direto em `src/faturama/interface/worker/runner.py` and `src/faturama/observability/logging.py`
- [X] T029 [US3] Atualizar a documentação do contrato de orquestração e do teste real em `specs/005-s3-eventbridge-ecs/contracts/orchestration.md`, `specs/005-s3-eventbridge-ecs/contracts/processing-message.md`, and `README.md`

**Checkpoint**: User Story 3 is complete when artifacts, status and logs remain traceable after the infrastructure simplification.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Fechar validação, documentação final e comandos de verificação.

- [X] T030 [P] Rodar e registrar a matriz de validação em `README.md` and `specs/005-s3-eventbridge-ecs/quickstart.md`
- [X] T031 [P] Atualizar referências remanescentes ao fluxo legado em `README.md`, `scripts/test_worker_from_ministack_s3.py`, `infra/terraform/environments/local/outputs.tf`, and `infra/terraform/modules/faturama_runtime/main.tf`
- [X] T032 Executar a verificação final da feature com `terraform -chdir=infra/terraform/environments/local validate`, `bash scripts/bootstrap_local_runtime.sh`, and `uv run scripts/test_worker_from_ministack_s3.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies and can start immediately.
- **Foundational (Phase 2)**: depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: depends on Foundational and is the MVP cut.
- **User Story 2 (Phase 4)**: depends on User Story 1 because it simplifies and stabilizes the provisioned runtime introduced there.
- **User Story 3 (Phase 5)**: depends on User Story 1 for direct dispatch and on User Story 2 for finalized runtime contracts and outputs.
- **Polish (Phase 6)**: depends on all stories selected for delivery.

### User Story Dependencies

- **US1**: starts after the foundational phase and has no dependency on other stories.
- **US2**: depends on the direct dispatch runtime from US1.
- **US3**: depends on the direct dispatch runtime from US1 and the cleaned runtime contract from US2.

### Within Each User Story

- Tests should be updated before the production files they validate.
- Terraform wiring should land before bootstrap and runtime documentation that depend on it.
- Runtime contract parsing should be stable before end-to-end validation.
- Each story ends with an independent validation checkpoint.

### Parallel Opportunities

- T002, T003, and T004 can run in parallel in Setup.
- T006, T007, T008, and T009 can run in parallel in Foundational.
- In US1, T010, T011, and T012 can run in parallel, then T013 and T014 can run in parallel before T015, T016, and T017.
- In US2, T018 and T019 can run in parallel, then T020 and T021 can run in parallel before T022 and T023.
- In US3, T024 and T025 can run in parallel, then T026 and T027 can run in parallel before T028 and T029.
- T030 and T031 can run in parallel after the stories are complete.

---

## Parallel Example: User Story 1

```bash
Task: "T010 Atualizar o teste e2e do dispatch para o caminho direto em tests/e2e/test_event_driven_dispatch_e2e.py"
Task: "T011 Atualizar o script de teste assíncrono real para observar EventBridge -> ECS em scripts/test_worker_from_ministack_s3.py"
Task: "T012 Atualizar a validação de contrato local do runtime em tests/e2e/test_local_runtime_contract.py"

Task: "T013 Criar a regra EventBridge do bucket de entrada com filtro preciso de chave em infra/terraform/modules/faturama_runtime/main.tf"
Task: "T014 Criar a role e o target EventBridge -> ECS RunTask com override do container worker em infra/terraform/modules/faturama_runtime/main.tf"
```

---

## Parallel Example: User Story 2

```bash
Task: "T018 Atualizar a validação Terraform do ambiente local em tests/e2e/test_local_runtime_contract.py and infra/terraform/environments/local/outputs.tf"
Task: "T019 Atualizar a checagem de provisionamento mínimo no quickstart em specs/005-s3-eventbridge-ecs/quickstart.md"

Task: "T020 Remover provider endpoints e dependências não usadas do ambiente local em infra/terraform/environments/local/main.tf"
Task: "T021 Remover provider archive e referências de artefato Lambda dos ambientes Terraform em infra/terraform/environments/local/main.tf and infra/terraform/environments/aws/main.tf"
```

---

## Parallel Example: User Story 3

```bash
Task: "T024 Atualizar os testes de regressão do pipeline assíncrono para remover dependência de Step Functions em tests/e2e/test_async_pipeline_regression.py"
Task: "T025 Atualizar os testes de persistência e status para a nova origem do comando em tests/integration/test_artifact_manifest_persistence.py, tests/integration/test_status_propagation_latency.py, and tests/integration/test_worker_failure_isolation.py"

Task: "T026 Persistir metadados de origem EventBridge na criação do job e do status em src/faturama/application/use_cases/process_processing_command.py and src/faturama/infrastructure/repositories/processing_job_repository.py"
Task: "T027 Atualizar a escrita do manifesto e a correlação dos artefatos com a tentativa real em src/faturama/application/services/artifact_manifest_service.py and src/faturama/application/services/artifact_key_builder.py"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate the real upload-driven dispatch before starting runtime cleanup or traceability refinements.

### Incremental Delivery

1. Deliver US1 to prove `S3 -> EventBridge -> ECS`.
2. Deliver US2 to make the infrastructure minimal and maintainable.
3. Deliver US3 to restore full traceability guarantees on top of the simplified path.
4. Finish with final validation and documentation updates.

### Parallel Team Strategy

1. One engineer can take Terraform/module cleanup while another updates runtime parsing and test fixtures during Foundational.
2. After Foundation, one engineer can own EventBridge/ECS wiring while another updates e2e validation and operational scripts for US1.
3. Once US1 lands, infrastructure cleanup and traceability refinement can proceed in parallel across US2 and US3 with coordination on shared docs and outputs.

---

## Notes

- `[P]` marks tasks that can proceed independently in the same phase.
- `[US1]`, `[US2]`, and `[US3]` map directly to the three user stories in `spec.md`.
- Every task includes exact file paths and uses the required checklist format.
- Suggested MVP scope: complete through T017, then run the independent validation for US1 before continuing.
