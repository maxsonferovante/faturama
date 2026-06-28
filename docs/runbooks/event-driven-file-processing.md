# Runbook: Event-Driven File Processing

## Objetivo

Operar e diagnosticar o runtime assíncrono de processamento de faturas baseado em `S3 -> SQS -> Pipe -> Step Functions -> ECS`.

## Checklist Operacional

1. Confirmar que o payload canônico contém `processing_id`, `bucket`, `object_key`, `event_time` e `source`.
2. Confirmar que o worker persiste `PENDING`, `RUNNING` e o estado final no read model.
3. Confirmar que o manifesto de artefatos foi gravado em `processados-faturama`.
4. Confirmar que `REVIEW_REQUIRED` permanece não terminal.

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
