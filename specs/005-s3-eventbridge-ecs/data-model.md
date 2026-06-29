# Data Model: S3 EventBridge ECS

## Overview

Esta feature simplifica o modelo operacional do dispatch. O processamento funcional da fatura continua no worker atual, mas o caminho de disparo deixa de depender de fila, lambda e state machine. O modelo principal passa a ser:

1. evento de criação do objeto no bucket de entrada;
2. transformação do evento em comando de processamento;
3. dispatch direto de uma task ECS;
4. persistência de status e artefatos já existentes na aplicação.

## Entities

### 1. SourceObjectEvent

**Purpose**: Representa o evento bruto `Object Created` emitido pelo bucket de entrada e recebido pela regra EventBridge.

**Fields**:

- `event_id`
- `event_time`
- `bucket_name`
- `object_key`
- `object_etag`
- `object_version`
- `object_size`
- `sequencer`
- `request_id`
- `requester`
- `reason`

**Validation Rules**:

- `bucket_name` deve corresponder ao bucket de entrada configurado.
- `object_key` deve atender ao prefixo de entrada definido.
- o sufixo do arquivo deve ser compatível com o tipo aceito para processamento.
- `event_id` deve ser preservado para rastreabilidade e deduplicação operacional.

### 2. EcsDispatchRequest

**Purpose**: Representa a chamada lógica que o EventBridge fará ao `ecs:RunTask`.

**Fields**:

- `dispatch_id`
- `cluster_arn`
- `task_definition_arn`
- `launch_type`
- `container_name`
- `processing_message`
- `target_role_arn`
- `requested_at`

**Validation Rules**:

- `dispatch_id` deve ser correlacionável ao `event_id` do `SourceObjectEvent`.
- `processing_message` deve obedecer ao contrato canônico consumido pelo worker.
- `target_role_arn` deve permitir `ecs:RunTask` e `iam:PassRole` apenas para os recursos necessários.

### 3. ProcessingCommand

**Purpose**: Representa o contrato canônico que entra no worker por variável de ambiente ou override de container.

**Fields**:

- `processing_id`
- `bucket`
- `object_key`
- `event_time`
- `source`
- `artifact_prefix`
- `metadata`

**Validation Rules**:

- `processing_id`, `bucket`, `object_key`, `event_time` e `source` são obrigatórios.
- `processing_id` deve ser derivado de forma rastreável do envelope do evento.
- `source` deve identificar que a origem foi um evento S3 recebido via EventBridge.
- `metadata` deve ser serializável e suportar `eventbridge_id`, `etag`, `version_id`, `sequencer` e outros campos opcionais relevantes.

### 4. ProcessingJob

**Purpose**: Representa a tentativa operacional persistida pela aplicação depois que o worker inicia.

**Fields**:

- `processing_id`
- `source_event_id`
- `current_status`
- `status_detail`
- `bucket_name`
- `object_key`
- `file_hash`
- `document_id`
- `requested_at`
- `started_at`
- `finished_at`
- `failure_code`
- `failure_message`

**Validation Rules**:

- `processing_id` deve ser único por tentativa.
- `source_event_id` deve permitir correlação com o evento recebido pelo EventBridge.
- `file_hash` continua sendo a base da identidade canônica do documento.
- `finished_at` só pode existir após transição para estado terminal.

### 5. ArtifactManifest

**Purpose**: Representa os artefatos produzidos pelo worker no bucket de saída.

**Fields**:

- `artifact_manifest_id`
- `processing_id`
- `artifact_bucket`
- `artifact_key_prefix`
- `source_pdf_uri`
- `markdown_uri`
- `json_uri`
- `result_uri`
- `artifact_status`
- `created_at`
- `updated_at`

**Validation Rules**:

- o manifesto deve apontar para o bucket de artefatos configurado.
- `artifact_key_prefix` deve ser correlacionável ao `processing_id`.
- `artifact_status` deve suportar `generated`, `partial`, `failed` e `reused`.

### 6. ProcessingStatusReadModel

**Purpose**: Representa a visão persistida de status consumida por outras interfaces da solução.

**Fields**:

- `processing_id`
- `document_id`
- `file_hash`
- `current_status`
- `is_terminal`
- `status_detail`
- `result_reference`
- `artifact_manifest_id`
- `last_transition_at`
- `updated_at`

**Validation Rules**:

- a visão deve poder ser atualizada sem depender de SQS ou Step Functions.
- `result_reference` deve apontar para o resultado final quando existente.
- `artifact_manifest_id` deve permitir recuperar os artefatos do processamento.

## Relationships

- Um `SourceObjectEvent` pode originar um `EcsDispatchRequest`.
- Um `EcsDispatchRequest` entrega exatamente um `ProcessingCommand` ao worker por tentativa.
- Um `ProcessingCommand` cria ou atualiza um `ProcessingJob`.
- Um `ProcessingJob` pode gerar zero ou um `ArtifactManifest`.
- Um `ProcessingJob` projeta exatamente um `ProcessingStatusReadModel` ativo por tentativa.

## State Transitions

### SourceObjectEvent

- `received` -> `matched`
- `received` -> `ignored`
- `matched` -> `dispatched`
- `matched` -> `dispatch_failed`

### ProcessingJob

- `PENDING` -> `RUNNING`
- `RUNNING` -> `SUCCESS`
- `RUNNING` -> `REVIEW_REQUIRED`
- `RUNNING` -> `PARTIAL`
- `RUNNING` -> `FAILED`
- `REVIEW_REQUIRED` -> `RUNNING`
- `REVIEW_REQUIRED` -> `FAILED`

## Removed Operational Entities

As seguintes entidades deixam de fazer parte do caminho principal desta feature:

- mensagem de fila SQS de processamento;
- execução Lambda de bridge;
- execução Step Functions de dispatch.

Elas deixam de ser centrais no modelo porque o dispatch passa a acontecer de forma direta entre EventBridge e ECS.
