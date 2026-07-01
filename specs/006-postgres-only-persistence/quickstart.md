# Quickstart: PostgreSQL Only Persistence

## Objective

Validar que o `faturama` roda apenas com PostgreSQL no ambiente local oficial, sem fallback SQLite em processamento, consultas CLI, review flow ou checkpoints.

## Prerequisites

- Docker e Docker Compose disponíveis
- dependências Python instaladas para o projeto
- `PYTHONPATH=src` para comandos locais de CLI/teste quando aplicável
- nenhuma variável pública `FATURAMA_DB_PATH` ou `FATURAMA_CHECKPOINT_DB_PATH` definida no shell de teste

## Local Runtime Setup

1. Subir o ambiente local oficial:

```bash
rtk docker compose up -d postgres
```

2. Exportar o DSN oficial usado pela CLI/testes locais:

```bash
export FATURAMA_DB_DSN=postgresql://faturama:faturama@localhost:5432/faturama
export FATURAMA_OPENDATALOADER_STUB_MODE=1
export FATURAMA_ARTIFACT_CACHE_DIR=$(pwd)/.tmp/artifacts
```

3. Executar o bootstrap/migração PostgreSQL da aplicação.

Expected outcome:
- schema PostgreSQL criado sem `PRAGMA`, sem arquivos `*.sqlite3` e sem migração oportunista baseada em SQLite.

## Validation Scenario 1: Configuration Fails Fast Without DSN

1. Limpar `FATURAMA_DB_DSN` do ambiente.
2. Executar um comando simples da CLI ou bootstrap da aplicação.

Expected outcome:
- a execução falha antes de abrir caso de uso ou repositório, com erro explícito sobre ausência de `FATURAMA_DB_DSN`.

## Validation Scenario 2: Process Invoice Uses PostgreSQL Only

1. Restaurar `FATURAMA_DB_DSN` com o valor oficial local.
2. Processar uma fatura de teste pela CLI principal.

Example shape:

```bash
PYTHONPATH=src python3 -m faturama.cli process-invoice --pdf-path <invoice.pdf> --user-id demo-user
```

Expected outcome:
- processamento concluído usando o DSN oficial
- documentos, statements, transações, parcelamentos, projeções, summaries, review items e decisões persistidos no PostgreSQL
- nenhum arquivo local de banco criado

## Validation Scenario 3: Read Queries Use the Same DSN

1. Com os dados já processados, executar os comandos de leitura principais:
- `list-statements`
- `show-statement`
- `list-transactions`
- `monthly-spend`
- `current-installments`
- `future-installments`
- `remaining-balance`
- `review-queue`

Expected outcome:
- todos os comandos respondem com base no PostgreSQL configurado por DSN
- nenhum comando exige ou deriva `database_path`

## Validation Scenario 4: Async Worker Uses the Same Backend and Checkpoints

1. Subir o ambiente do worker local conforme `docker-compose.yml`:

```bash
rtk docker compose up -d postgres ministack worker
```

2. Disparar o fluxo assíncrono suportado para um documento de teste.
3. Observar status operacional e retomada de checkpoint após interrupção controlada.

Expected outcome:
- `processing_jobs`, `processing_status_read_model`, `artifact_manifests` e `workflow_checkpoints` usam o mesmo PostgreSQL oficial
- `review_required` e restauração de checkpoint continuam funcionais sem `langgraph.checkpoint.sqlite`

## Validation Scenario 5: Regression Sweep for SQLite Removal

Run a repository search for banned legacy markers in productive code:

```bash
rtk rg -n "sqlite|sqlite3|\.sqlite3|FATURAMA_DB_PATH|FATURAMA_CHECKPOINT_DB_PATH|INSERT OR REPLACE|PRAGMA|langgraph.checkpoint.sqlite|langgraph-checkpoint-sqlite" src pyproject.toml README.md docs tests
```

Expected outcome:
- nenhuma ocorrência em código produtivo
- ocorrências restantes, se houver, ficam restritas a documentação histórica de migração explicitamente justificada

## Related Contracts

- [Persistence Ports](./contracts/persistence-ports.md)
- [Bootstrap Composition](./contracts/bootstrap-composition.md)
- [Runtime Configuration](./contracts/runtime-config.md)
- [Data Model](./data-model.md)
