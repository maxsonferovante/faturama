# Contract: Processing Message

## Objective

Definir o payload canônico que o EventBridge deve entregar ao worker ECS por override de container.

## Payload

```json
{
  "processing_id": "evtbridge-17793124-05d4-b198-2fde-7ededc63b103",
  "bucket": "pre-processamento-faturama",
  "object_key": "incoming/fatura.pdf",
  "event_time": "2021-11-12T00:00:00Z",
  "source": "aws.s3.eventbridge",
  "artifact_prefix": "processed",
  "metadata": {
    "eventbridge_id": "17793124-05d4-b198-2fde-7ededc63b103",
    "etag": "b1946ac92492d2347c6235b4d2611184",
    "version_id": "IYV3p45BT0ac8hjHg1houSdS1a.Mro8e",
    "sequencer": "617f08299329d189",
    "request_id": "N4N7GDK58NMKJ12R",
    "requester": "123456789012",
    "reason": "PutObject"
  }
}
```

## Field Rules

- `processing_id`: identificador da tentativa; deve ser derivado de forma rastreável do `id` do evento.
- `bucket`: bucket de entrada onde o PDF foi criado.
- `object_key`: chave exata do PDF no bucket de entrada.
- `event_time`: timestamp do evento S3 recebido pelo EventBridge.
- `source`: origem lógica do dispatch; deve distinguir este caminho do fluxo legado.
- `artifact_prefix`: prefixo sob o qual o worker publicará seus artefatos.
- `metadata`: metadados auxiliares da origem; campos extras podem ser adicionados sem quebrar compatibilidade.

## Serialization Rules

- O payload deve ser serializado como JSON válido.
- O valor final deve ser entregue ao container pela variável `FATURAMA_PROCESSING_MESSAGE`.
- Campos novos em `metadata` não podem quebrar o parsing do worker.
- O worker deve continuar tratando `processing_id` como tentativa e o hash do PDF como identidade canônica do documento.
