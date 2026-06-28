# Data Model: Processamento Assincrono de Faturas por Eventos

## Overview

Esta feature adiciona uma camada operacional distribuída sobre o pipeline já existente e move o estado durável do ambiente assíncrono para armazenamento compartilhado:

1. autorização de upload e ingestão do evento de objeto;
2. despacho assíncrono de processamento;
3. ledger de status, retries e polling;
4. artefatos duráveis e checkpoints resumíveis;
5. persistência canônica já conhecida pela solução.

As entidades canônicas de fatura, transação, parcelamento, projeção, decisão e revisão continuam válidas, mas passam a depender de adapters PostgreSQL/S3 quando executadas no runtime assíncrono.

## Entities

### 1. UploadAuthorizationGrant

**Purpose**: Representa a autorização temporária que permitiu um upload externo no bucket de entrada.

**Fields**:

- `upload_grant_id`
- `authorized_bucket`
- `authorized_object_key`
- `granted_to`
- `granted_by`
- `granted_at`
- `expires_at`
- `upload_completed_at`
- `grant_status`
- `trace_context`

**Validation Rules**:

- `expires_at` deve ser posterior a `granted_at`.
- `authorized_object_key` deve apontar para um prefixo elegível para PDFs de entrada.
- `grant_status` deve suportar `issued`, `used`, `expired`, `revoked`.
- um upload consumido deve permanecer vinculável ao grant que o originou.

### 2. SourceObjectEvent

**Purpose**: Representa o evento recebido a partir do upload de um PDF no bucket de entrada.

**Fields**:

- `source_event_id`
- `bucket_name`
- `object_key`
- `object_version`
- `event_time`
- `event_name`
- `object_etag`
- `upload_grant_id`
- `source_system`
- `received_at`
- `dedupe_key`

**Validation Rules**:

- `bucket_name` deve corresponder ao bucket de entrada configurado para o ambiente.
- `object_key` deve apontar para um PDF elegível para processamento.
- `dedupe_key` deve ser estável o suficiente para reconhecer reentregas equivalentes do mesmo evento de armazenamento.
- quando o upload vier de URL assinada, `upload_grant_id` deve conseguir correlacionar o objeto com a autorização temporária correspondente.

### 3. ProcessingJob

**Purpose**: Representa a execução lógica do processamento assíncrono de um documento.

**Fields**:

- `processing_id`
- `source_event_id`
- `execution_arn`
- `dispatch_attempt`
- `current_status`
- `status_detail`
- `bucket_name`
- `object_key`
- `document_id`
- `file_hash`
- `requested_at`
- `started_at`
- `finished_at`
- `failure_code`
- `failure_message`
- `runtime_environment`

**Validation Rules**:

- `processing_id` deve ser único por execução lógica do fluxo.
- `current_status` deve suportar pelo menos `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`, além de estados operacionais internos como `DISPATCHING`, `REVIEW_REQUIRED` e `PARTIAL`.
- `finished_at` só pode existir quando o job atingir estado terminal.
- `dispatch_attempt` deve crescer monotonicamente em retentativas explícitas.
- `processing_id` identifica a tentativa, enquanto `file_hash` identifica o documento canônico para deduplicação.
- `REVIEW_REQUIRED` não pode ser tratado como estado terminal.

### 4. ProcessingCommand

**Purpose**: Representa o contrato canônico entregue ao worker ECS para iniciar o processamento.

**Fields**:

- `processing_id`
- `bucket`
- `object_key`
- `event_time`
- `source`
- `metadata`
- `artifact_prefix`
- `trace_id`
- `requested_by`
- `upload_grant_id`

**Validation Rules**:

- `processing_id`, `bucket`, `object_key`, `event_time` e `source` são obrigatórios.
- `source` deve suportar pelo menos `s3`.
- `metadata` deve ser serializável e opcionalmente conter valores como `object_version`, `etag`, `sqs_message_id` e ambiente.
- `upload_grant_id` deve existir quando a origem tiver vindo de URL assinada emitida pelo contexto maior.

### 5. ArtifactManifest

**Purpose**: Representa os artefatos duráveis produzidos ou reutilizados durante o processamento de um PDF.

**Fields**:

- `artifact_manifest_id`
- `processing_id`
- `artifact_bucket`
- `source_pdf_uri`
- `markdown_uri`
- `json_uri`
- `result_uri`
- `artifact_key_prefix`
- `artifact_status`
- `checksum`
- `created_at`
- `updated_at`

**Validation Rules**:

- todo manifesto deve pertencer a um `ProcessingJob`;
- `artifact_bucket` deve ser `processados-faturama` na v1;
- `artifact_key_prefix` deve ser rastreável até o `processing_id`, o `document_id` ou outro identificador canônico equivalente;
- `artifact_status` deve suportar `generated`, `reused`, `partial`, `failed`;
- `source_pdf_uri` deve permanecer imutável para o mesmo `processing_id`.

### 6. WorkflowCheckpointSnapshot

**Purpose**: Representa um snapshot persistido do workflow para retomada após revisão ou falha parcial.

**Fields**:

- `checkpoint_id`
- `processing_id`
- `workflow_thread_id`
- `node_name`
- `checkpoint_status`
- `state_payload`
- `state_payload_ref`
- `review_required`
- `created_at`
- `restored_at`

**Validation Rules**:

- cada checkpoint deve estar vinculado a um único `ProcessingJob`;
- `checkpoint_status` deve suportar `active`, `restored`, `superseded`, `completed`;
- `state_payload` ou `state_payload_ref` deve permitir reconstrução determinística do ponto de retomada;
- checkpoints só podem ser restaurados se o job ainda não estiver em estado terminal definitivo.

### 7. ReviewHold

**Purpose**: Representa uma interrupção operacional aberta por ambiguidade ou inconsistência que exige decisão rastreável.

**Fields**:

- `review_hold_id`
- `processing_id`
- `entity_type`
- `entity_id`
- `reason_code`
- `reason_detail`
- `confidence_snapshot`
- `status`
- `resolution_source`
- `resolution_payload`
- `opened_at`
- `resolved_at`

**Validation Rules**:

- `status` deve suportar `open`, `resolved`, `reapplied`, `expired`;
- uma resolução só pode ser aplicada a um hold ainda aberto ou reaproveitável;
- `resolution_payload` deve preservar contexto suficiente para reaplicar a decisão sem reinterpretar o PDF inteiro.
- a existência de um `ReviewHold` aberto deve manter o `ProcessingJob` em `REVIEW_REQUIRED`, não em estado terminal.

### 8. CanonicalPersistenceBatch

**Purpose**: Representa o resultado consolidado da persistência canônica disparada pelo worker após o processamento.

**Fields**:

- `persistence_batch_id`
- `processing_id`
- `document_id`
- `statement_count`
- `transaction_count`
- `installment_plan_count`
- `projection_count`
- `review_items_opened`
- `result_status`
- `persisted_at`

**Validation Rules**:

- `result_status` deve suportar `SUCCESS`, `REVIEW_REQUIRED`, `PARTIAL`, `FAILED`;
- os contadores devem ser coerentes com o que foi de fato persistido;
- um `ProcessingJob` só deve apontar para um lote canônico ativo por tentativa concluída.

### 9. ProcessingStatusReadModel

**Purpose**: Representa a visão persistida de status consumida pela outra API do contexto maior.

**Fields**:

- `processing_id`
- `document_id`
- `file_hash`
- `current_status`
- `is_terminal`
- `status_detail`
- `result_reference`
- `artifact_manifest_id`
- `review_required`
- `last_transition_at`
- `updated_at`

**Validation Rules**:

- a visão deve ser derivada do `ProcessingJob` sem exigir leitura direta de logs do worker;
- `is_terminal` só pode ser verdadeiro para `SUCCESS`, `PARTIAL` ou `FAILED`;
- `review_required` deve ser verdadeiro quando o estado exposto for `REVIEW_REQUIRED`;
- `result_reference` deve apontar para o resultado canônico, quando já existir, ou permanecer vazio de forma explícita.
- `artifact_manifest_id` deve permitir que a API de status ou auditoria recupere as referências persistidas dos artefatos OpenDataLoader quando existirem.

## Relationships

- Um `UploadAuthorizationGrant` pode originar zero ou um `SourceObjectEvent` consumido.
- Um `SourceObjectEvent` pode originar um ou mais `ProcessingJob` em caso de reprocessamento controlado.
- Um `ProcessingJob` gera exatamente um `ProcessingCommand`.
- Um `ProcessingJob` pode gerar zero ou um `ArtifactManifest`.
- Um `ProcessingJob` pode gerar múltiplos `WorkflowCheckpointSnapshot`.
- Um `ProcessingJob` pode abrir múltiplos `ReviewHold`.
- Um `ProcessingJob` termina em zero ou um `CanonicalPersistenceBatch`.
- Um `ProcessingJob` projeta exatamente uma `ProcessingStatusReadModel` ativa por tentativa.
- `CanonicalPersistenceBatch` referencia as entidades canônicas já existentes na solução, agora persistidas via adapters compatíveis com PostgreSQL.

## State Transitions

### ProcessingJob

- `PENDING` → `DISPATCHING`
- `DISPATCHING` → `RUNNING`
- `RUNNING` → `REVIEW_REQUIRED`
- `REVIEW_REQUIRED` → `RUNNING`
- `RUNNING` → `SUCCESS`
- `RUNNING` → `PARTIAL`
- `PENDING|DISPATCHING|RUNNING|REVIEW_REQUIRED` → `FAILED`

### UploadAuthorizationGrant

- `issued` → `used`
- `issued` → `expired`
- `issued` → `revoked`

### WorkflowCheckpointSnapshot

- `active` → `restored`
- `active` → `completed`
- `active` → `superseded`

### ReviewHold

- `open` → `resolved`
- `resolved` → `reapplied`
- `open` → `expired`

## Mapping Notes

- O `ProcessingCommand` é a tradução do evento bruto de armazenamento para o contrato interno do worker.
- `UploadAuthorizationGrant` fecha a rastreabilidade entre a URL assinada emitida a um integrador e o objeto realmente enviado.
- `ProcessingJob.current_status` é o estado operacional de referência para integrações externas e observabilidade.
- `ProcessingStatusReadModel` é a superfície persistida que a outra API deve usar para consulta de status, em vez de ler diretamente o runtime de execução.
- `ArtifactManifest` representa o vínculo auditável entre a execução e os arquivos gravados em `processados-faturama`.
- `CanonicalPersistenceBatch.result_status` reflete o resultado do processamento do ponto de vista dos dados canônicos e pode divergir temporariamente de `current_status` durante a execução.
- Os modelos canônicos existentes para faturas, transações, parcelamentos, projeções, summaries, decisões e review items devem ser preservados semanticamente, mesmo que a implementação mude de SQLite para PostgreSQL.
