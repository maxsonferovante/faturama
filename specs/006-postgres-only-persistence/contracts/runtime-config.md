# Contract: Runtime Configuration

## Goal

Definir um contrato público de configuração coerente com PostgreSQL único para CLI, worker, testes locais e bootstrap operacional.

## Required Public Variables

### `FATURAMA_DB_DSN`

**Status**: required

**Purpose**: única fonte de configuração do banco transacional oficial para processamento, consultas, review flow e checkpoints.

**Accepted shape**:
- `postgresql://...`
- `postgres://...`

**Rejected shape**:
- `sqlite:///...`
- caminhos de arquivo `.sqlite3` ou `.db`
- valor ausente ou vazio

## Optional Variables Still In Scope

These remain valid when used by the application, but none of them define an alternate database backend:
- runtime environment selectors
- AWS/Ministack endpoint variables
- bucket and artifact prefix variables
- OpenDataLoader variables
- observability/log-level variables

## Public Variables Removed from Supported Contract

The following variables must stop being documented and stop influencing productive code paths:
- `FATURAMA_DB_PATH`
- `FATURAMA_CHECKPOINT_DB_PATH`

If an explicit checkpoint backend selector is later introduced, it must reference only real supported strategies and cannot imply filesystem SQLite fallback.

## Validation Behavior

`load_settings()` or equivalent configuration loader must:
- fail fast when `FATURAMA_DB_DSN` is missing
- fail fast when the scheme is not PostgreSQL-compatible
- produce a clear operator-facing error message
- never silently choose a local fallback

## Local Runtime Contract

The local official environment is `docker-compose.yml`, which already provides:
- `postgres:16-alpine`
- `worker` with `FATURAMA_DB_DSN=postgresql://faturama:faturama@postgres:5432/faturama`

CLI, worker and tests must converge on this same contract.
