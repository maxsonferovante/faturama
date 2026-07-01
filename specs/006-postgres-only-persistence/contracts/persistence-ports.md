# Contract: Persistence Ports

## Goal

Definir o contrato mínimo que permite à aplicação deixar de importar `sqlite.py`, `postgres.py`, `sqlite3.Connection` e repositórios concretos diretamente, mantendo a refatoração focada em PostgreSQL único.

## Required Application Ports

### `UnitOfWorkFactory`

Creates one persistence scope for write use cases.

**Responsibilities**:
- open one PostgreSQL connection/session
- start transaction lifecycle
- expose repository instances needed by the use case
- expose checkpoint store access when required
- commit or rollback atomically
- close the underlying connection

**Expected operations**:
- `open() -> UnitOfWork`

### `UnitOfWork`

Represents one transactional write boundary.

**Responsibilities**:
- provide repositories for canonical persistence
- provide repositories for async operational persistence
- provide checkpoint store when the workflow needs durable state
- provide explicit `commit()` and `rollback()`
- close resources deterministically

**Expected repository access**:
- documents/statements
- transactions
- installment plans and projections
- summaries
- review items
- decisions
- evidences
- processing jobs/status/manifests when relevant to the use case
- checkpoint store

### `CheckpointStore`

PostgreSQL-only durable workflow state contract.

**Required methods**:
- `save(job_id, thread_id, node_name, state, checkpoint_status='active', review_required=False) -> checkpoint_id`
- `latest(job_id) -> checkpoint | None`
- `mark_restored(checkpoint_id) -> None`

**Rules**:
- backed only by PostgreSQL
- no local filesystem path parameter
- payload returned by `latest` must already be decoded into application-usable structure

### `ReadModelQueryService` or explicit read ports

Supports CLI/query handlers without exposing raw connections.

**Required capabilities**:
- list statements with period/card filters
- fetch one statement by id
- list transactions by statement with optional filters
- list monthly summaries
- list current installments by month
- list future installments by month
- calculate remaining balance by plan or card
- list pending review items and resolve one item

**Rules**:
- application query handlers receive this service or narrower ports
- direct `repo.connection.execute(...)` is forbidden

## Required Repository Behavior Changes

### Upsert semantics

All repositories that currently use `INSERT OR REPLACE` must expose deterministic PostgreSQL upsert behavior using explicit conflict targets.

### Commit ownership

Repository methods must stop calling `commit()` internally. Transaction ownership belongs to `UnitOfWork`.

### Driver typing

Concrete repositories must stop typing constructor dependencies as `sqlite3.Connection` and instead depend on the PostgreSQL execution surface chosen by infrastructure.

## Current Gap Map

The following current patterns must disappear from productive code:
- `from sqlite3 import Connection`
- constructors typed as `Connection`
- SQL placeholders `?`
- `INSERT OR REPLACE`
- caller-owned `connect(Path(...))`
- caller-owned `connect_from_dsn(...)` in application/query modules
- direct raw SQL through `repo.connection.execute(...)`

## Acceptance Shape

A code search after implementation should show:
- application modules depend only on ports and DTO/domain types
- PostgreSQL SQL is isolated in infrastructure repositories and bootstrap/migration modules
- interface modules own composition of settings, factories and runtime wiring
