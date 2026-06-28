# Implementation Plan: Alinhamento de Runtime da Arquitetura

**Branch**: `[main]` | **Date**: 2026-06-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-align-runtime-architecture/spec.md`

## Summary

Restabelecer o runtime oficial do pipeline de faturas para que a ingestão execute de verdade com `OpenDataLoader PDF` na extração primária e `LangGraph` na orquestração com checkpoints e revisão assistida, preservando a persistência canônica em SQLite, a idempotência e as consultas já prometidas na `001-invoice-extractor`.

## Technical Context

**Language/Version**: Python 3.12+ no contrato do projeto; `pyproject.toml` atual já exige `>=3.12`

**Primary Dependencies**: `langgraph`, `langgraph-checkpoint-sqlite`, `opendataloader-pdf[hybrid]`, `langchain-opendataloader-pdf`, `pydantic`, biblioteca padrão

**Storage**: SQLite para base canônica e checkpoints locais do workflow; arquivos locais para PDFs de entrada e artefatos extraídos em Markdown/JSON

**Testing**: `pytest` para testes unitários, de integração, contrato de CLI e e2e do pipeline oficial

**Target Platform**: CLI local em Linux/macOS com Python 3.12+ e Java 11+ disponível no `PATH`

**Project Type**: Pipeline/CLI Python com Clean Architecture e fluxo documental auditável

**Performance Goals**: Processar uma fatura digital suportada no fluxo oficial em menos de 60 segundos em ambiente local padrão; retomar uma execução interrompida por revisão sem reprocessar artefatos primários; manter consultas persistidas em menos de 5 segundos

**Constraints**: `OpenDataLoader` deve substituir sidecars pré-gerados como fonte primária; `LangGraph` deve coordenar checkpoints, transições e human-in-the-loop real; IA só entra em casos ambíguos; side effects anteriores a pausas precisam ser idempotentes; valores observados e projetados permanecem separados

**Scale/Scope**: v1 cobre o fluxo principal de ingestão individual e em lote, fila de revisão, retomada e consultas existentes para um histórico pessoal com dezenas a centenas de faturas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Pythonic Correctness and Readability`: PASS. O plano mantém adapters pequenos para extração, workflow, checkpoints e revisão, com contratos tipados e responsabilidades explícitas.
- `Clean Architecture Boundaries`: PASS. `LangGraph`, `OpenDataLoader` e integração LangChain ficam confinados à infraestrutura e à orquestração de aplicação; domínio e consultas permanecem independentes.
- `Object-Oriented Design and SOLID`: PASS. O desenho separa extração primária, estado do workflow, revisão assistida, persistência e read models em responsabilidades distintas.
- `Testable Design and Quality Gates`: PASS. A feature exige testes unitários para roteamento/estado, integração para extração/checkpoint, contrato para CLI e e2e para ingestão com revisão.
- `Simplicity, Observability, and Operational Reliability`: PASS. O fluxo oficial continua local e auditável, com checkpoints SQLite, logs estruturados, uso condicional de IA e eliminação de atalhos paralelos.

## Project Structure

### Documentation (this feature)

```text
specs/003-align-runtime-architecture/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   └── workflow.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── faturama/
    ├── application/
    │   ├── ports/
    │   ├── services/
    │   ├── dto/
    │   ├── queries/
    │   └── use_cases/
    ├── domain/
    │   ├── entities/
    │   ├── services/
    │   ├── value_objects/
    │   └── exceptions.py
    ├── infrastructure/
    │   ├── config/
    │   ├── database/
    │   ├── files/
    │   ├── llm/
    │   ├── opendataloader/
    │   └── repositories/
    ├── interface/
    │   └── cli/
    ├── observability/
    └── shared/

tests/
├── contract/
├── e2e/
├── integration/
└── unit/
```

**Structure Decision**: Manter a estrutura Python em `src/` e encaixar a correção do runtime no desenho existente. A orquestração oficial entra na camada de aplicação, `OpenDataLoader` e a integração LangChain entram na infraestrutura, e a CLI continua a única interface externa da v1.

## Phase 0: Research Summary

As decisões de pesquisa foram consolidadas em [research.md](./research.md) com foco em: usar `StateGraph`/`compile` como workflow oficial, usar `interrupt` e checkpoints SQLite para revisão e retomada, usar `opendataloader_pdf.convert(...)` como extração canônica e usar `OpenDataLoaderPDFLoader` para fornecer contexto estruturado ao ramo assistido por IA quando a regra não bastar.

## Phase 1: Design Summary

- O modelo de dados da correção foi definido em [data-model.md](./data-model.md), cobrindo job oficial, artefatos extraídos, checkpoints, casos de revisão e resolução assistida.
- Os contratos operacionais foram definidos em [contracts/cli.md](./contracts/cli.md) e [contracts/workflow.md](./contracts/workflow.md).
- O fluxo de validação local e ponta a ponta foi documentado em [quickstart.md](./quickstart.md), incluindo extração real, pausa por revisão e retomada.
- O bloco gerenciado do agente deve apontar para este plano após a atualização de contexto.

## Post-Design Constitution Check

- `Pythonic Correctness and Readability`: PASS. Os artefatos preservam contratos explícitos, nomes coesos e separação entre adapters e regras.
- `Clean Architecture Boundaries`: PASS. O desenho mantém dependências externas fora do domínio e encapsula o workflow em serviços de aplicação e infraestrutura.
- `Object-Oriented Design and SOLID`: PASS. O plano separa estado do workflow, extração, decisão assistida e persistência em componentes especializados.
- `Testable Design and Quality Gates`: PASS. O desenho induz testes por camada e por fluxo observável, incluindo regressão contra o atalho de sidecars.
- `Simplicity, Observability, and Operational Reliability`: PASS. Checkpoints SQLite, interrupções explícitas, artefatos determinísticos e retomada idempotente mantêm o fluxo operacional previsível.

## Complexity Tracking

No constitution violations requiring justification.
