# Implementation Plan: Relatório de Uso

**Branch**: `[002-usage-report]` | **Date**: 2026-06-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-usage-report/spec.md`

## Summary

Construir uma implementação real no projeto para diagnosticar o uso efetivo de componentes planejados versus componentes apenas declarados, com execução por CLI e materialização em Markdown. A v1 cobre LangGraph, OpenDataLoader e sinais estruturais centrais do pipeline atual, produzindo evidências rastreáveis, desvios de aderência e correções automáticas apenas quando houver contexto suficiente para uma ação segura e auditável.

## Technical Context

**Language/Version**: Python 3.12+ no padrão da constituição; repositório já configurado com `src/` layout

**Primary Dependencies**: biblioteca padrão, `pytest` para validação, parsing local do repositório existente e utilitários de observabilidade já presentes no projeto; sem dependência obrigatória de SDK externo na v1 da análise

**Storage**: Arquivo Markdown materializado no repositório e leitura do código-fonte local como fonte de evidência

**Testing**: pytest com testes unitários, de integração, contrato de CLI e fluxo ponta a ponta

**Target Platform**: CLI local em ambiente Linux/macOS para mantenedores do projeto

**Project Type**: Ferramenta CLI interna acoplada ao projeto Python existente

**Performance Goals**: Gerar diagnóstico focado da v1 em menos de 10 segundos em checkout local padrão; produzir saída legível e arquivo Markdown na mesma execução

**Constraints**: Escopo inicial restrito a LangGraph, OpenDataLoader e sinais estruturais centrais do pipeline; correção automática apenas por opt-in explícito e somente quando defensável e rastreável; sem extrapolar conclusões globais fora do escopo definido

**Scale/Scope**: Análise de um único repositório local, poucas integrações prioritárias, uso primário por mantenedores e revisores técnicos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Pythonic Correctness and Readability`: PASS. A feature será implementada como CLI e serviços pequenos, com contratos explícitos e documentação testável.
- `Clean Architecture Boundaries`: PASS. A análise pode ficar em domínio/aplicação/interface sem acoplar regras a infraestrutura externa.
- `Object-Oriented Design and SOLID`: PASS. O problema pede classificadores, evidências, desvios e correções como responsabilidades separadas.
- `Testable Design and Quality Gates`: PASS. O plano já prevê testes unitários, integração, contrato e e2e para o relatório.
- `Simplicity, Observability, and Operational Reliability`: PASS. Escopo focado, sem dependência externa obrigatória, com rastreabilidade explícita de evidências, decisões e sinais operacionais mínimos.

## Project Structure

### Documentation (this feature)

```text
specs/002-usage-report/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── faturama/
    ├── domain/
    │   ├── entities/
    │   ├── services/
    │   └── value_objects/
    ├── application/
    │   ├── use_cases/
    │   ├── queries/
    │   ├── services/
    │   └── ports/
    ├── interface/
    │   └── cli/
    ├── infrastructure/
    │   ├── files/
    │   ├── config/
    │   └── repositories/
    └── observability/

tests/
├── contract/
├── integration/
├── unit/
└── e2e/

docs/
└── runbooks/
```

**Structure Decision**: Manter a estrutura Clean Architecture já existente no repositório. A nova feature entra como comando CLI, serviços de análise/classificação/correção, artefatos Markdown e testes distribuídos por tipo de validação.

## Phase 0: Research Summary

As decisões de pesquisa foram consolidadas em [research.md](./research.md) com foco em: CLI + Markdown como entrega principal, escopo inicial restrito aos componentes críticos já apontados no diagnóstico, critério rigoroso para “uso real” baseado em código executável, política conservadora para correção automática por opt-in e necessidade de observabilidade mínima da execução.

## Phase 1: Design Summary

- O modelo de dados foi definido em [data-model.md](./data-model.md) cobrindo alvo analisado, evidência, conclusão de uso, desvio de especificação e ação corretiva.
- O contrato externo da feature foi definido em [contracts/cli.md](./contracts/cli.md) para o comando `usage-report`.
- O fluxo de validação ponta a ponta foi documentado em [quickstart.md](./quickstart.md), incluindo geração padrão, materialização explícita, remediação opt-in e validação operacional.
- O contexto gerenciado do agente foi atualizado para apontar para este plano.

## Post-Design Constitution Check

- `Pythonic Correctness and Readability`: PASS. Os artefatos assumem contratos claros, nomenclatura explícita e documentação validável.
- `Clean Architecture Boundaries`: PASS. A feature permanece separada entre domínio, aplicação, interface e infraestrutura.
- `Object-Oriented Design and SOLID`: PASS. A modelagem distribui responsabilidades entre evidência, achado, desvio e ação corretiva.
- `Testable Design and Quality Gates`: PASS. O plano exige cobertura por testes unitários, integração, contrato e e2e.
- `Simplicity, Observability, and Operational Reliability`: PASS. O escopo permanece pequeno, auditável, com política explícita para automação segura e sinais mínimos de execução previstos no desenho.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
