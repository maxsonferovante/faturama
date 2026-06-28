# Tasks: Relatório de Uso

**Input**: Design documents from `/specs/002-usage-report/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Testes são obrigatórios nesta feature por exigência explícita do plano, do quickstart e da constituição do projeto.

**Organization**: Tasks agrupadas por user story para permitir implementação incremental, validação independente e entrega de MVP a partir da US1.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependência direta)
- **[Story]**: Mapeia tarefa à user story correspondente (`[US1]`, `[US2]`, `[US3]`)
- Todas as descrições incluem caminhos exatos de arquivo

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar estrutura e entrypoints da feature no projeto existente

- [X] T001 Update CLI registration in `src/faturama/cli.py` to add the `usage-report` command group
- [X] T002 Create command module skeleton in `src/faturama/interface/cli/usage_report.py`
- [X] T003 [P] Create feature package markers in `src/faturama/domain/entities/__init__.py`, `src/faturama/domain/services/__init__.py`, `src/faturama/application/use_cases/__init__.py`, and `src/faturama/application/services/__init__.py` if missing for new imports
- [X] T004 [P] Create default output-path and parent-directory handling contract in `docs/runbooks/usage-report.md` and reserve default materialization path conventions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Entregar o núcleo compartilhado da análise e da remediação antes das histórias

**⚠️ CRITICAL**: Nenhuma user story deve começar antes do fim desta fase

- [X] T005 Define domain entities for analysis targets and findings in `src/faturama/domain/entities/analysis_target.py`, `src/faturama/domain/entities/evidence_record.py`, `src/faturama/domain/entities/usage_finding.py`, `src/faturama/domain/entities/specification_deviation.py`, and `src/faturama/domain/entities/remediation_action.py`
- [X] T006 [P] Define value objects and enums for classifications and severity in `src/faturama/domain/value_objects/usage_classification.py`, `src/faturama/domain/value_objects/evidence_kind.py`, and `src/faturama/domain/value_objects/deviation_severity.py`
- [X] T007 [P] Define DTOs for report output and materialized sections in `src/faturama/application/dto/usage_report_dto.py`, `src/faturama/application/dto/usage_finding_dto.py`, and `src/faturama/application/dto/remediation_dto.py`
- [X] T008 [P] Define ports for repository inspection, report writing, and safe remediation in `src/faturama/application/ports/repository_inspector.py`, `src/faturama/application/ports/report_writer.py`, and `src/faturama/application/ports/remediation_service.py`
- [X] T009 Implement repository scanning primitives in `src/faturama/infrastructure/files/repository_reader.py`
- [X] T010 [P] Implement evidence collection helpers for file excerpts and line references in `src/faturama/application/services/evidence_collector.py`
- [X] T011 [P] Implement Markdown materialization adapter in `src/faturama/infrastructure/files/usage_report_writer.py`
- [X] T012 Implement foundational integration tests for repository reading, report writing, and output path handling in `tests/integration/test_repository_reader.py`, `tests/integration/test_usage_report_writer.py`, and `tests/integration/test_usage_report_paths.py`
- [X] T013 Implement structured logging, execution metrics, and explicit error reporting in `src/faturama/observability/logging.py`, `src/faturama/observability/metrics.py`, `src/faturama/application/use_cases/generate_usage_report.py`, and `src/faturama/interface/cli/usage_report.py`
- [X] T014 [P] Add integration coverage for operational signals and CLI error semantics in `tests/integration/test_usage_report_observability.py`

**Checkpoint**: Entidades, portas, leitura de repositório e escrita do relatório prontas para iniciar as histórias

---

## Phase 3: User Story 1 - Publicar diagnóstico confiável do estado atual (Priority: P1) 🎯 MVP

**Goal**: Executar um comando real do projeto que analisa o escopo da v1, classifica os componentes e materializa um relatório Markdown coerente com a saída operacional

**Independent Test**: Rodar `python3 -m faturama.cli usage-report --format json` em um checkout local e validar classificação, evidências e geração do Markdown

### Tests for User Story 1

- [X] T015 [P] [US1] Create contract test for `usage-report` output shape in `tests/contract/test_cli_usage_report.py`
- [X] T016 [P] [US1] Create integration test for focused component analysis and Markdown materialization in `tests/integration/test_usage_report_generation.py`
- [X] T017 [P] [US1] Create unit tests for usage classification rules in `tests/unit/test_usage_classifier.py`

### Implementation for User Story 1

- [X] T018 [P] [US1] Implement target catalog for LangGraph, OpenDataLoader, and pipeline signals in `src/faturama/application/services/analysis_catalog.py`
- [X] T019 [P] [US1] Implement executable-usage detection service in `src/faturama/domain/services/usage_classifier.py`
- [X] T020 [P] [US1] Implement focused repository inspection service in `src/faturama/application/services/repository_analysis.py`
- [X] T021 [P] [US1] Implement finding assembly service in `src/faturama/application/services/finding_builder.py`
- [X] T022 [US1] Implement usage report generation use case in `src/faturama/application/use_cases/generate_usage_report.py`
- [X] T023 [US1] Implement `usage-report` CLI command in `src/faturama/interface/cli/usage_report.py`
- [X] T024 [US1] Integrate the new command into CLI dispatch in `src/faturama/cli.py`

**Checkpoint**: A US1 deve gerar diagnóstico operacional confiável e Markdown materializado sem depender das demais histórias

---

## Phase 4: User Story 2 - Evidenciar desvios entre especificação e implementação (Priority: P2)

**Goal**: Comparar comportamento observado com expectativa declarada e produzir desvios materiais com evidências e impacto

**Independent Test**: Executar o relatório em um cenário com integrações apenas declaradas e validar a emissão de desvios com classificação e razão explícitas

### Tests for User Story 2

- [X] T025 [P] [US2] Create contract test for deviation fields in CLI output and Markdown in `tests/contract/test_cli_usage_report_deviations.py`
- [X] T026 [P] [US2] Create integration test for specification-versus-code deviation detection in `tests/integration/test_usage_report_deviations.py`
- [X] T027 [P] [US2] Create unit tests for evidence ranking and deviation severity in `tests/unit/test_evidence_ranking.py` and `tests/unit/test_deviation_severity.py`

### Implementation for User Story 2

- [X] T028 [P] [US2] Implement expected-behavior extraction service from active spec and plan in `src/faturama/application/services/expectation_loader.py`
- [X] T029 [P] [US2] Implement evidence ranking service in `src/faturama/domain/services/evidence_ranker.py`
- [X] T030 [P] [US2] Implement deviation detection service in `src/faturama/domain/services/deviation_detector.py`
- [X] T031 [P] [US2] Implement severity evaluation and summary generation in `src/faturama/application/services/deviation_reporting.py`
- [X] T032 [US2] Extend usage report use case to include deviations and impact analysis in `src/faturama/application/use_cases/generate_usage_report.py`
- [X] T033 [US2] Extend Markdown writer to render deviations, evidence, and rationale in `src/faturama/infrastructure/files/usage_report_writer.py`

**Checkpoint**: A US2 deve produzir diagnóstico comparativo claro entre expectativa e comportamento observado

---

## Phase 5: User Story 3 - Apoiar decisão de remediação ou replanejamento (Priority: P3)

**Goal**: Permitir correção automática segura quando houver contexto suficiente e registrar follow-up manual quando não houver

**Independent Test**: Rodar `python3 -m faturama.cli usage-report --fix-when-safe --format json` e validar correções aplicadas ou pendências manuais rastreadas

### Tests for User Story 3

- [X] T034 [P] [US3] Create contract test for remediation fields in CLI output in `tests/contract/test_cli_usage_report_remediation.py`
- [X] T035 [P] [US3] Create integration test for safe auto-fix flow and deferred manual follow-up in `tests/integration/test_usage_report_remediation.py`
- [X] T036 [P] [US3] Create unit tests for remediation eligibility and safe patch planning in `tests/unit/test_remediation_policy.py` and `tests/unit/test_safe_patch_planner.py`

### Implementation for User Story 3

- [X] T037 [P] [US3] Implement remediation eligibility policy in `src/faturama/domain/services/remediation_policy.py`
- [X] T038 [P] [US3] Implement safe patch planning service in `src/faturama/application/services/safe_patch_planner.py`
- [X] T039 [P] [US3] Implement concrete remediations for in-scope deviations in `src/faturama/infrastructure/files/usage_report_remediator.py`
- [X] T040 [P] [US3] Implement manual follow-up recording and rendering in `src/faturama/application/services/remediation_reporting.py`
- [X] T041 [US3] Extend usage report use case with `--fix-when-safe` flow in `src/faturama/application/use_cases/generate_usage_report.py`
- [X] T042 [US3] Extend CLI argument handling and exit semantics for safe remediation in `src/faturama/interface/cli/usage_report.py`

**Checkpoint**: A US3 deve fechar o ciclo operacional de diagnóstico, correção segura e escalonamento manual

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Completar documentação, endurecer qualidade e validar o fluxo inteiro

- [X] T043 [P] Add end-to-end regression suite for generation, deviation detection, and remediation in `tests/e2e/test_usage_report_e2e.py`
- [X] T044 [P] Add performance and stability tests for focused analysis runtime in `tests/integration/test_usage_report_performance.py`
- [X] T045 Update user-facing documentation for the feature in `README.md` and `docs/runbooks/usage-report.md`
- [X] T046 Run and document the quickstart scenarios in `specs/002-usage-report/quickstart.md`
- [X] T047 Review terminology and output consistency across CLI, Markdown, and spec references in `src/faturama/interface/cli/usage_report.py`, `src/faturama/infrastructure/files/usage_report_writer.py`, and `docs/runbooks/usage-report.md`
- [X] T048 [P] Add readability validation for the materialized report structure in `tests/integration/test_usage_report_readability.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: começa imediatamente
- **Phase 2: Foundational**: depende da conclusão da Setup e bloqueia todas as histórias
- **Phase 3: US1**: depende da conclusão da Foundational
- **Phase 4: US2**: depende da conclusão da Foundational e se integra ao motor de geração da US1
- **Phase 5: US3**: depende da conclusão da Foundational e do fluxo de desvios da US2
- **Phase 6: Polish**: depende das histórias desejadas concluídas

### User Story Dependencies

- **US1 (P1)**: nenhuma dependência de outras histórias; forma o MVP
- **US2 (P2)**: depende de US1 para ter análise e materialização base
- **US3 (P3)**: depende de US2 para operar sobre desvios identificados

### Within Each User Story

- Testes vêm antes da implementação principal
- Catálogo e modelos antes dos serviços de aplicação
- Serviços de domínio antes dos use cases
- Use cases antes dos comandos CLI
- Escrita final de Markdown após os serviços de montagem do diagnóstico

### Parallel Opportunities

- Setup: `T003`, `T004`
- Foundational: `T006`, `T007`, `T008`, `T010`, `T011`, `T014`
- US1: `T015`, `T016`, `T017`, `T018`, `T019`, `T020`, `T021`
- US2: `T025`, `T026`, `T027`, `T028`, `T029`, `T030`, `T031`
- US3: `T034`, `T035`, `T036`, `T037`, `T038`, `T039`, `T040`
- Polish: `T043`, `T044`, `T048`

---

## Parallel Example: User Story 1

```bash
# Tests for US1
Task: "T015 [US1] Create contract test for usage-report output in tests/contract/test_cli_usage_report.py"
Task: "T016 [US1] Create integration test for generation and Markdown materialization in tests/integration/test_usage_report_generation.py"
Task: "T017 [US1] Create unit tests for usage classification rules in tests/unit/test_usage_classifier.py"

# Core analysis services for US1
Task: "T018 [US1] Implement target catalog in src/faturama/application/services/analysis_catalog.py"
Task: "T019 [US1] Implement executable-usage detection service in src/faturama/domain/services/usage_classifier.py"
Task: "T020 [US1] Implement repository inspection service in src/faturama/application/services/repository_analysis.py"
Task: "T021 [US1] Implement finding assembly service in src/faturama/application/services/finding_builder.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1
4. Validate `usage-report` end to end against `quickstart.md`
5. Stop and review before adding deviation analysis and remediation

### Incremental Delivery

1. Setup + Foundational
2. US1 for diagnóstico operacional e materialização
3. US2 para detecção formal de desvios
4. US3 para correção segura e follow-up manual
5. Polish para documentação, performance e regressão

### Parallel Team Strategy

1. Team fecha Setup + Foundational
2. Depois da Foundational:
   - Developer A: US1 geração e materialização
   - Developer B: US2 desvios e severidade
   - Developer C: US3 remediação segura
3. Reunificar em Phase 6 para e2e e performance

---

## Notes

- Todas as tasks seguem o formato obrigatório com checkbox, ID, marcador `[P]` quando aplicável, label de story e caminho de arquivo
- A implementação deve respeitar as camadas da constituição: domínio sem dependência de CLI ou infraestrutura externa
- A US1 é o escopo sugerido de MVP
