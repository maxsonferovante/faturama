# Contract: Orchestration Flow

## Purpose

Definir o contrato lógico entre bucket, fila, pipe, Step Function e ECS para o processamento assíncrono de PDFs.

## Canonical Flow

1. Um sistema do contexto maior emite uma URL assinada temporária para um objeto permitido no bucket `pre-processamento-faturama`.
2. O cliente externo faz `PUT` do PDF nessa URL.
3. O bucket publica um evento `ObjectCreated` para uma fila SQS standard.
4. Um EventBridge Pipe consome a fila, aplica filtros necessários e inicia a Step Function.
5. A Step Function normaliza o evento em um `ProcessingCommand`.
6. A Step Function executa `ecs:runTask` sem `.sync`.
7. O worker ECS baixa o PDF, processa a fatura, salva os artefatos OpenDataLoader em `processados-faturama` e persiste status, manifesto e resultado.
8. Outra API do contexto maior consulta o estado persistido no banco para acompanhar `RUNNING`, `REVIEW_REQUIRED`, `SUCCESS`, `PARTIAL` ou `FAILED`.

## State Machine Expectations

A state machine da v1 deve possuir, no mínimo, estes estados lógicos:

1. `NormalizeSourceEvent`
2. `BuildProcessingCommand`
3. `RunWorkerTask`
4. `FinishDispatch`

## ECS Dispatch Rules

- o estado `RunWorkerTask` deve usar `arn:aws:states:::ecs:runTask`;
- a execução não deve usar `.sync`;
- parâmetros devem ser enviados ao container por override explícito de ambiente ou comando;
- o payload enviado ao worker deve obedecer a [processing-message.md](./processing-message.md).

## Retry and Failure Semantics

- falhas antes do `RunWorkerTask` devem manter contexto suficiente para reenfileiramento controlado ou DLQ;
- falhas na chamada `ecs:RunTask` devem marcar a execução como falha de dispatch;
- falhas internas do worker não retroagem a Step Function já concluída; elas são observadas no ledger do processamento e nos logs;
- falhas na gravação dos artefatos em `processados-faturama` devem impedir que a execução seja marcada como sucesso completo;
- eventos duplicados devem produzir no máximo um resultado canônico ativo para o mesmo documento, ainda que haja mais de uma tentativa operacional;
- novas tentativas para o mesmo conteúdo devem gerar novo `processing_id`, mas não nova identidade canônica do documento.

## Queue and Pipe Semantics

- a fila deve ser SQS standard na v1;
- o pipe deve ter um único consumo oficial da fila para evitar competição entre consumidores;
- filtros do pipe devem garantir que apenas mensagens de PDFs elegíveis iniciem a state machine;
- a configuração de DLQ deve capturar mensagens que excederem a política de retentativa do consumo assíncrono.

## Observability Contract

- cada execução deve ser correlacionável por `processing_id`;
- a Step Function deve permitir localizar o `processing_id` e a chave S3 normalizada;
- a task ECS deve registrar `processing_id`, `bucket`, `object_key` e estado final;
- `REVIEW_REQUIRED` deve permanecer visível como estado pendente não terminal no read model de status;
- não existe evento externo obrigatório de conclusão na v1; o canal oficial para consumidores é a API de status apoiada no banco;
- diferenças de observabilidade entre ambiente local e AWS real devem ser documentadas em `quickstart.md` e `runtime-config.md`.
