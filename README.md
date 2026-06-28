# Faturama

Pipeline local para extracao auditavel de faturas de cartao, persistencia em SQLite e consultas por CLI sobre gasto mensal, parcelas observadas, saldo parcelado e fila de revisao.

## Stack

- Python com estrutura `src/`
- Persistencia SQLite
- Contratos Pydantic com fallback local
- `LangGraph` como workflow oficial com checkpoints SQLite
- `OpenDataLoader PDF` como extracao primaria de PDF em runtime
- `OpenDataLoaderPDFLoader` no ramo assistido por IA para contexto semantico
- Suite `pytest` cobrindo contrato, integracao, unidade e e2e

## Comandos principais

```bash
python3 -m faturama.cli process-invoice --pdf-path samples/invoice-2026-04.pdf --user-id demo-user
python3 -m faturama.cli monthly-spend --user-id demo-user --month 2026-04
python3 -m faturama.cli future-installments --user-id demo-user --month 2026-05
python3 -m faturama.cli review-queue --user-id demo-user
```

## Variaveis uteis

- `FATURAMA_DB_PATH`: base canonica SQLite
- `FATURAMA_CHECKPOINT_DB_PATH`: base SQLite dos checkpoints
- `FATURAMA_ARTIFACT_CACHE_DIR`: cache de artefatos `markdown/json` gerados em runtime
- `FATURAMA_OPENDATALOADER_HYBRID_URL`: endpoint opcional do modo hibrido
- `FATURAMA_AGENT_AUTO_APPLY_THRESHOLD`: limiar alto para autoaplicacao pelo agente
- `FATURAMA_OPENDATALOADER_STUB_MODE=1`: modo de teste com fixtures locais

## Politicas operacionais

- o runtime oficial nao depende de sidecars preparados manualmente para producao; os artefatos `.md/.json` sao gerados ou reutilizados como cache do proprio pipeline
- historico legado nao-oficial e marcado como `invalidated`, ficando fora das consultas ate reconstrucao manual
- revisoes resolvidas podem ser reaplicadas em novo processamento do mesmo documento para o workflow continuar sem reabrir a mesma pendencia

## Estrutura resumida

- `src/faturama/domain`: entidades, value objects e regras de parsing/matching
- `src/faturama/application`: use cases, queries, DTOs e estado do workflow
- `src/faturama/infrastructure`: SQLite, cache de artefatos, adapters OpenDataLoader e contexto LLM
- `src/faturama/interface/cli`: superficie de comandos da v1
- `tests/`: suites unit, integration, contract e e2e
- `docs/runbooks/`: operacao do pipeline oficial e validacao de performance

## Validacao

```bash
python3 -m pytest -q
```

Validacao local mais recente do checkout em `2026-06-27`: `49 passed`.
