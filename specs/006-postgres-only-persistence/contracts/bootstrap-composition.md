# Contract: Bootstrap Composition

## Goal

Mover a composição de dependências para a borda da aplicação, de modo que CLI, worker e demais entrypoints montem explicitamente o backend PostgreSQL oficial e entreguem portas prontas aos casos de uso.

## Composition Root Responsibilities

### CLI composition

A camada `interface/cli` deve:
- carregar configuração válida
- construir a fábrica PostgreSQL oficial
- montar query services ou read ports
- injetar dependências nos handlers de leitura e revisão
- reutilizar o mesmo DSN oficial do processamento
- concentrar a composição de leitura em um módulo dedicado, como `src/faturama/interface/cli/composition.py`, em vez de espalhar wiring pelos handlers

### Worker composition

A camada `interface/worker` deve:
- carregar configuração válida
- construir a fábrica PostgreSQL oficial
- montar o caso de uso de processamento assíncrono com repositórios, object storage e checkpoint store corretos
- falhar rápido se o DSN estiver ausente ou inválido

### Processing composition

O caso de uso principal de processamento deve ser construído por composição externa.

**Target shape**:
- `process_invoice` receives ports or a unit of work factory
- `process_processing_command` receives ports or a unit of work factory
- workflow node factories consume repository/checkpoint abstractions instead of importing SQLite/PostgreSQL helpers directly

## Minimal Suggested Module Layout

```text
src/faturama/
  application/
    ports/
      repositories.py
      unit_of_work.py
      checkpoint_store.py
  infrastructure/
    database/
      postgres.py
      migrations/
    repositories/
      postgres_*.py
    checkpoint/
      postgres_checkpoint_store.py
  interface/
    cli/
      composition.py
    worker/
      composition.py
```

The exact filenames can vary, but the ownership boundary must remain the same: application knows interfaces, infrastructure knows PostgreSQL, interface wires everything.

## Lifecycle Contract

### Configuration
- validate before any repository or runtime is built
- reject missing `FATURAMA_DB_DSN`
- reject SQLite-like schemes and file-path fallbacks

### Connection lifecycle
- one place opens `psycopg` connections
- one place configures row factories and transaction settings
- one place closes them

### Transaction lifecycle
- write use cases open one unit of work
- repository methods do not finalize transactions
- failure in any persistence step rolls back the full unit

## Anti-Patterns Explicitly Removed

The following composition patterns are out of contract after this feature:
- use case importing `faturama.infrastructure.database.sqlite`
- use case choosing between `connect_from_dsn(...)` and `connect(...)`
- queries deriving `_db_path()` from settings
- runtime/checkpoint objects created from local filesystem paths
