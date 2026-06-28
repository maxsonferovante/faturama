# Contract: Processing Message

## Purpose

Definir o payload canônico entregue ao worker ECS para iniciar o processamento de uma fatura enviada ao bucket de entrada.

## Contract Owner

- produtor lógico: Step Function após normalizar o evento vindo do S3/SQS
- consumidor: entrypoint do worker em `src/faturama/interface/worker`

## Canonical Payload

```json
{
  "bucket": "pre-processamento-faturama",
  "object_key": "incoming/fatura-2026-04.pdf",
  "event_time": "2026-06-28T12:00:00Z",
  "processing_id": "evt-20260628-0001",
  "source": "s3",
  "upload_grant_id": "grant-20260628-001",
  "metadata": {
    "object_version": "string-opcional",
    "etag": "string-opcional",
    "sqs_message_id": "string-opcional",
    "trace_id": "string-opcional",
    "requestor_ref": "string-opcional"
  }
}
```

## Required Rules

- `bucket` deve corresponder ao bucket configurado para o ambiente ativo.
- `object_key` deve apontar para um PDF elegível para ingestão.
- `event_time` deve preservar o timestamp observado do evento de origem ou, quando necessário, o timestamp de normalização explicitamente documentado.
- `processing_id` deve ser único por tentativa lógica do processamento.
- `source` deve ser `s3` na v1.
- `upload_grant_id` deve existir quando o upload tiver sido feito por URL assinada emitida pelo contexto maior.
- `metadata` deve aceitar campos adicionais sem quebrar consumidores existentes.

## Normalization Rules

- o evento bruto vindo do S3/SQS permanece como envelope de transporte e evidência, não como contrato de aplicação;
- a Step Function deve extrair o bucket e a chave do primeiro registro elegível;
- o `processing_id` deve ser derivado de identificador único estável da execução, preferencialmente o identificador da execução da Step Function;
- a identidade canônica do documento não faz parte do contrato de entrada e deve ser calculada pelo worker via hash do PDF;
- `metadata` deve carregar apenas dados auxiliares de rastreabilidade, sem duplicar campos obrigatórios no nível raiz.

## Worker Expectations

- o worker deve validar o payload antes de baixar o arquivo do S3;
- falha de validação deve levar o job a `FAILED` com causa explícita;
- o worker deve registrar `processing_id`, `bucket` e `object_key` como chave mínima de rastreabilidade em logs e persistência operacional;
- o worker deve gravar os artefatos OpenDataLoader em `processados-faturama` usando uma chave rastreável antes de concluir a execução com sucesso;
- o worker deve tratar reprocessamentos do mesmo documento de forma idempotente com base no hash do PDF e nas chaves canônicas já existentes.
