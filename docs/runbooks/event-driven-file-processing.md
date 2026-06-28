# Runbook: Event-Driven File Processing

## Objetivo

Operar e diagnosticar o runtime assíncrono de processamento de faturas baseado em `S3 -> SQS -> Pipe -> Step Functions -> ECS`.

## Checklist Operacional

1. Confirmar que o payload canônico contém `processing_id`, `bucket`, `object_key`, `event_time` e `source`.
2. Confirmar que o worker persiste `PENDING`, `RUNNING` e o estado final no read model.
3. Confirmar que o manifesto de artefatos foi gravado em `processados-faturama`.
4. Confirmar que `REVIEW_REQUIRED` permanece não terminal.
5. Confirmar que a imagem local `faturama-worker:local` foi buildada antes do dispatch ECS emulado.

## Bootstrap Local

Use o bootstrap único do repositório:

```bash
bash scripts/bootstrap_local_runtime.sh
```

Ordem executada:

1. sobe `postgres` e `ministack` via Compose;
2. builda a imagem `faturama-worker:local`;
3. executa `terraform init -backend=false`;
4. executa `terraform apply -auto-approve`.

Observação:

- no ambiente local, o MiniStack acessa o daemon Docker do host via `/var/run/docker.sock`; por isso o ECS emulado enxerga a imagem local buildada com a tag esperada pela task definition.
- o PostgreSQL local nao precisa de porta publicada no host para este fluxo; a comunicacao do worker acontece pela network Docker do projeto.
- se a porta `4566` estiver ocupada, use `MINISTACK_PORT=4567 bash scripts/bootstrap_local_runtime.sh`.

## Diagnóstico de Falhas

### Upload aceito, mas processamento não iniciou

- verificar presença do objeto em `pre-processamento-faturama`
- verificar dedupe key e reentregas no ledger de eventos de origem
- verificar se a tentativa ficou presa em `PENDING` ou `DISPATCHING`

### Worker falhou durante a execução

- localizar `processing_id` nos logs estruturados
- verificar `failure_code`, `failure_message` e `status_detail`
- confirmar se o read model foi atualizado para `FAILED`

### Resultado ausente ou parcial

- consultar o manifesto persistido do `processing_id`
- verificar `artifact_status`
- validar `result_reference` e `artifact_manifest_id` no read model

## Comandos de Verificação

```bash
python3 -m pytest
python3 -m pytest tests/e2e/test_operational_diagnostics.py
python3 -m pytest tests/e2e/test_async_sla.py tests/e2e/test_async_concurrency_burst.py
```

## Critérios de Aceite Operacional

- status visível em até 30 segundos no ambiente local de validação
- conclusão de documento elegível abaixo de 5 minutos
- burst de 20 uploads elegíveis com pelo menos 90% de sucesso operacional
