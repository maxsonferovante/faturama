# Implementation Plan: Extrator de Faturas Estruturadas

**Branch**: `main` | **Date**: 2026-06-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-invoice-extractor/spec.md`

## Summary

Construir a v1 de um pipeline Python para ingestão de faturas de cartão em PDF, extração híbrida com predominância determinística, consolidação de lançamentos e parcelamentos em um modelo canônico auditável, persistência em SQLite e consultas operacionais por CLI para gastos mensais, parcelas cobradas, parcelas futuras e saldo parcelado, com revisão manual obrigatória para todo item abaixo do limiar de confiança e chave canônica inicial de parcelamento baseada em descrição normalizada, valor da parcela, cartão e data de origem aproximada.

## Technical Context

**Language/Version**: Python 3.14 no repositório atual, mantendo compatibilidade com as regras da constituição para Python 3.12+

**Primary Dependencies**: `opendataloader-pdf[hybrid]` para extração base de PDF, `pydantic` para contratos, `langgraph` para orquestração com checkpoints, biblioteca padrão para hashing e arquivos, driver SQLite nativo

**Storage**: SQLite como base canônica v1 para documentos, faturas, transações, planos parcelados, projeções, itens de revisão e registros de decisão

**Testing**: `pytest` para testes unitários, de integração, contrato e fluxo ponta a ponta; validação de consultas via fixtures com faturas de exemplo

**Target Platform**: Ambiente local ou servidor Linux executando pipeline batch e consultas por CLI

**Project Type**: Pipeline/CLI de processamento documental com read model analítico local

**Performance Goals**: Processar uma fatura suportada individual em menos de 60 segundos em ambiente local padrão; responder consultas analíticas persistidas em menos de 5 segundos

**Constraints**: LLM usada apenas para ambiguidade; modelo canônico independente do emissor; rastreabilidade obrigatória por linha; todo item abaixo do limiar de confiança deve abrir revisão manual; reprocessamento idempotente; separação explícita entre observado e projetado; categorias detalhadas de gasto ficam fora da v1

**Scale/Scope**: v1 orientada a histórico individual por usuário, dezenas a centenas de faturas, múltiplos emissores progressivamente suportados, centenas de transações por competência

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Pythonic Correctness and Readability`: PASS. O plano assume tipagem explícita, contratos claros e centralização de configuração em `pyproject.toml`.
- `Clean Architecture Boundaries`: PASS. O desenho separa domínio financeiro, orquestração de casos de uso, adaptadores de CLI e infraestrutura de PDF/SQLite/LLM.
- `Object-Oriented Design and SOLID`: PASS. O plano evita agente monolítico e favorece objetos/serviços pequenos com responsabilidades bem definidas.
- `Testable Design and Quality Gates`: PASS. O plano exige testes unitários, integração, contrato e e2e para ingestão, matching, projeção e consultas.
- `Simplicity, Observability, and Operational Reliability`: PASS. SQLite e CLI reduzem escopo; decisões e confiança são persistidas; falhas e reprocessamento têm tratamento explícito.

## Project Structure

### Documentation (this feature)

```text
specs/001-invoice-extractor/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   └── read-model.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── faturama/
    ├── domain/
    │   ├── entities/
    │   ├── services/
    │   ├── value_objects/
    │   └── exceptions.py
    ├── application/
    │   ├── dto/
    │   ├── ports/
    │   ├── queries/
    │   ├── services/
    │   ├── use_cases/
    │   └── unit_of_work.py
    ├── interface/
    │   └── cli/
    ├── infrastructure/
    │   ├── database/
    │   ├── files/
    │   ├── llm/
    │   ├── opendataloader/
    │   └── repositories/
    ├── observability/
    └── shared/

tests/
├── contract/
├── e2e/
├── integration/
└── unit/
```

**Structure Decision**: Adotar a estrutura Clean Architecture prescrita pela constituição, usando CLI como interface inicial e mantendo integrações de PDF, LLM e SQLite exclusivamente na infraestrutura.

## Phase 0: Research Summary

As decisões de pesquisa foram consolidadas em [research.md](./research.md) com foco em: base canônica SQLite, CLI como interface v1, política de confiança com precedência de evidência estrutural e revisão obrigatória abaixo do limiar, matching conservador de parcelamentos com chave canônica inicial explícita e materializações analíticas mínimas para consultas mensais e futuras.

## Phase 1: Design Summary

- O modelo canônico foi definido em [data-model.md](./data-model.md) cobrindo documento, fatura, evidência, transação, plano parcelado, ocorrência, projeção, resumo mensal, item de revisão e registro de decisão, incluindo regras explícitas para chave canônica de parcelamento e revisão manual abaixo do limiar.
- Os contratos expostos ao usuário foram definidos em [contracts/cli.md](./contracts/cli.md) e [contracts/read-model.md](./contracts/read-model.md).
- O fluxo de validação e uso manual foi documentado em [quickstart.md](./quickstart.md).
- O contexto gerenciado do agente deve apontar para este plano após a geração dos artefatos.

## Post-Design Constitution Check

- `Pythonic Correctness and Readability`: PASS. Os artefatos assumem tipos explícitos e fronteiras coesas.
- `Clean Architecture Boundaries`: PASS. O modelo e os contratos mantêm domínio desacoplado de CLI, SQLite, extração de PDF e LLM.
- `Object-Oriented Design and SOLID`: PASS. Parcelamento, projeção, decisão de confiança e revisão são tratados como entidades e serviços distintos.
- `Testable Design and Quality Gates`: PASS. Quickstart e contratos explicitam cenários testáveis e estrutura de suites.
- `Simplicity, Observability, and Operational Reliability`: PASS. O plano mantém v1 pequena, auditável e com persistência local previsível.

## Complexity Tracking

No constitution violations requiring justification.
