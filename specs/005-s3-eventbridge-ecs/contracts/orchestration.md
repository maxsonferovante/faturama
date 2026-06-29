# Contract: Orchestration

## Objective

Definir o contrato do caminho real de dispatch `S3 -> EventBridge -> ECS RunTask` para o processamento assíncrono de PDFs.

## Event Source Contract

O trigger oficial do processamento é um evento de serviço do Amazon S3 entregue ao EventBridge com:

- `source = "aws.s3"`
- `detail-type = "Object Created"`

Campos relevantes do payload de origem:

```json
{
  "id": "17793124-05d4-b198-2fde-7ededc63b103",
  "detail-type": "Object Created",
  "source": "aws.s3",
  "time": "2021-11-12T00:00:00Z",
  "detail": {
    "bucket": {
      "name": "pre-processamento-faturama"
    },
    "object": {
      "key": "incoming/fatura.pdf",
      "etag": "b1946ac92492d2347c6235b4d2611184",
      "version-id": "IYV3p45BT0ac8hjHg1houSdS1a.Mro8e",
      "sequencer": "617f08299329d189"
    },
    "request-id": "N4N7GDK58NMKJ12R",
    "requester": "123456789012",
    "reason": "PutObject"
  }
}
```

## Event Pattern Contract

A regra de dispatch deve combinar, no mínimo:

```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {
      "name": ["pre-processamento-faturama"]
    },
    "object": {
      "key": [
        { "wildcard": "incoming/*.pdf" }
      ]
    }
  }
}
```

## Notes

- O valor exato do bucket deve vir do Terraform do ambiente.
- Se a implementação final preferir `prefix` ou `suffix` em vez de `wildcard`, a regra final ainda deve permanecer equivalente em precisão e evitar disparos sobre arquivos fora do escopo.
- O bucket de artefatos não participa dessa regra.

## Target Contract

O target da regra deve:

- invocar diretamente `ecs:RunTask`;
- apontar para o cluster ECS do runtime;
- usar a task definition do worker;
- passar um override para o container `worker`;
- injetar `FATURAMA_PROCESSING_MESSAGE` com o payload canônico do processamento.

## Dispatch Evidence Contract

Uma execução válida do fluxo deve produzir evidência observável em pelo menos dois pontos:

1. criação de uma task/container do worker após o upload elegível;
2. criação de artefatos sob o prefixo configurado no bucket `processados-faturama`.

Essas evidências são o mínimo exigido para considerar o teste ponta a ponta bem-sucedido.

## Local Emulator Caveat

Na validacao local com MiniStack `1.3.69`, o target ECS fica registrado no EventBridge, mas:

- o upload real no bucket nao gerou evidência de dispatch ate o worker;
- um evento publicado manualmente no EventBridge nao despachou `ecs:RunTask`.

O log observado no segundo caso foi:

```text
EventBridge: unsupported target type for ARN arn:aws:ecs:us-east-1:000000000000:cluster/faturama-cluster
```

Portanto, a ausência de task ECS nesse ambiente especifico nao indica erro no contrato Terraform desta feature.
