# Implementation Plan: PostgreSQL Only Persistence

**Branch**: `[]` | **Date**: 2026-06-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-postgres-only-persistence/spec.md`

## Summary

Consolidar o `faturama` em PostgreSQL único, removendo totalmente SQLite do código produtivo, da configuração pública, dos checkpoints, da CLI e dos testes, e reposicionando a composição de dependências para uma borda explícita baseada em portas, unidade de trabalho e adapters PostgreSQL nativos.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: `psycopg[binary]`, `pydantic`, `langgraph`, `boto3`, Docker Compose, Terraform já existente para runtime local/worker; remoção explícita da dependência legada `langgraph-checkpoint-sqlite`

**Storage**: PostgreSQL único para dados canônicos, read models operacionais e checkpoints resumíveis; S3 compatível para PDFs e artefatos processados

**Testing**: `pytest`, testes de integração/contrato/e2e contra PostgreSQL real em container, `docker compose`, validação CLI com `PYTHONPATH=src`

**Target Platform**: CLI Python local, worker container local, runtime assíncrono em ECS local compatível via Docker + MiniStack

**Project Type**: backend Python orientado a workflow com CLI e worker assíncrono

**Performance Goals**: manter o processamento ponta a ponta funcional no ambiente local oficial via `docker-compose`; preservar retomada por checkpoint e consultas CLI sem regressão perceptível de latência operacional

**Constraints**: não introduzir nova camada multi-banco; remover SQLite antes de generalizar abstrações; toda persistência oficial deve usar o mesmo DSN PostgreSQL; checkpoints e read models não podem gravar em arquivos locais; dados SQLite legados não podem permanecer como fallback de runtime; documentação local deve refletir um único caminho suportado

**Scale/Scope**: refatoração transversal em `src/`, `tests/`, `docs/`, `README.md`, `pyproject.toml` e specs ativas; cobre processamento síncrono, worker assíncrono, review flow, queries CLI, bootstrap de schema e suíte local

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Pythonic Correctness and Readability`: PASS. O plano remove camadas de compatibilidade implícita e substitui fallback silencioso por contratos explícitos e mais legíveis.
- `Clean Architecture Boundaries`: PASS com ação corretiva obrigatória. O estado atual viola a fronteira ao importar infraestrutura concreta nos use cases e queries; a própria feature existe para restaurar essas bordas.
- `Object-Oriented Design and SOLID`: PASS. O desenho alvo reduz acoplamento, introduz apenas contratos mínimos orientados a caso de uso e evita abstrações genéricas multi-banco.
- `Testable Design and Quality Gates`: PASS. O plano exige migração dos testes para PostgreSQL real e falha rápida de configuração, reduzindo falsos positivos de compatibilidade.
- `Simplicity, Observability, and Operational Reliability`: PASS. A simplificação principal é remoção de duplicidade arquitetural; o caminho oficial passa a ser único e observável.

## Project Structure

### Documentation (this feature)

```text
specs/006-postgres-only-persistence/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── bootstrap-composition.md
│   ├── persistence-ports.md
│   └── runtime-config.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── faturama/
    ├── application/
    │   ├── ports/
    │   ├── queries/
    │   ├── services/
    │   └── use_cases/
    ├── infrastructure/
    │   ├── config/
    │   ├── database/
    │   ├── external_services/
    │   └── repositories/
    ├── interface/
    │   ├── cli/
    │   └── worker/
    └── observability/

tests/
├── contract/
├── e2e/
├── integration/
└── unit/

docs/
├── runbooks/
└── database-schema.md
```

**Structure Decision**: A refatoração fica concentrada em `application/ports`, `application/use_cases`, `application/queries`, `infrastructure/database`, `infrastructure/repositories`, `interface/cli`, `interface/worker` e `tests`, com atualização de `README.md`, `docs/` e `pyproject.toml`. O objetivo é mover a composição de dependências para a borda de interface e manter a aplicação dependente apenas de contratos PostgreSQL-only.

## Phase 0: Research Summary

As decisões de pesquisa foram consolidadas em [research.md](./research.md) com foco em: remover completamente o fallback SQLite em vez de expandir compatibilidade; usar `psycopg` de forma nativa com unidade de trabalho e lifecycle centralizado; substituir bootstrap dinâmico por migração versionada ou DDL PostgreSQL explícito de bootstrap; persistir checkpoints na mesma base oficial; e migrar testes/docs para o ambiente local oficial baseado em `docker-compose` com PostgreSQL.

## Phase 1: Design Summary

- O modelo de dados e os agregados operacionais impactados pela remoção de SQLite foram definidos em [data-model.md](./data-model.md).
- Os contratos de portas de persistência, composição/bootstrap e configuração de runtime foram definidos em [contracts/persistence-ports.md](./contracts/persistence-ports.md), [contracts/bootstrap-composition.md](./contracts/bootstrap-composition.md) e [contracts/runtime-config.md](./contracts/runtime-config.md).
- O guia de validação local foi documentado em [quickstart.md](./quickstart.md), cobrindo `docker compose`, bootstrap do schema PostgreSQL, execução da CLI, worker assíncrono e verificação dos critérios de remoção de SQLite.
- O contexto do agente deve ser repontado para este plano após a geração dos artefatos.

## Post-Design Constitution Check

- `Pythonic Correctness and Readability`: PASS. O design reduz branches implícitos de runtime e troca caminhos legados por interfaces explícitas e composição clara.
- `Clean Architecture Boundaries`: PASS. Use cases e queries passam a depender de portas e unidade de trabalho, enquanto `psycopg`, SQL PostgreSQL e bootstrap ficam confinados à infraestrutura/interface.
- `Object-Oriented Design and SOLID`: PASS. Os contratos novos são mínimos e orientados a responsabilidades reais: unidade de trabalho, checkpoint store e serviços de leitura.
- `Testable Design and Quality Gates`: PASS. A validação passa a usar PostgreSQL real e elimina fixtures que mascaravam incompatibilidades por `sqlite:///`.
- `Simplicity, Observability, and Operational Reliability`: PASS. A arquitetura final tem um único backend oficial, menos caminhos de erro silencioso e um bootstrap previsível.

## Complexity Tracking

No constitution violations requiring justification.
