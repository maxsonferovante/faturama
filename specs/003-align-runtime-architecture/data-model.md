# Data Model: Alinhamento de Runtime da Arquitetura

## Overview

O desenho desta feature adiciona uma camada operacional sobre o modelo canônico já existente:

1. execução oficial do workflow;
2. artefatos de extração gerados em runtime;
3. pausas, retomadas e checkpoints;
4. casos de revisão assistida;
5. resultado canônico já conhecido pela `001-invoice-extractor`.

## Entities

### 1. RuntimeIngestionJob

**Purpose**: Representa uma execução oficial do pipeline de ingestão sob coordenação do workflow.

**Fields**:

- `job_id`
- `user_id`
- `source_pdf_path`
- `document_id`
- `workflow_status`
- `started_at`
- `updated_at`
- `completed_at`
- `active_checkpoint_id`
- `resume_token`
- `failure_reason`

**Validation Rules**:

- `job_id` deve ser único por execução iniciada.
- `workflow_status` deve suportar pelo menos `initialized`, `extracting`, `parsing`, `awaiting_review`, `persisting`, `completed`, `failed`.
- `resume_token` só pode existir quando a execução estiver pausada ou reentrante.

### 2. ExtractedDocumentArtifact

**Purpose**: Representa o resultado bruto da extração primária gerada pelo `OpenDataLoader` para um documento.

**Fields**:

- `artifact_id`
- `job_id`
- `document_id`
- `source_pdf_path`
- `markdown_path`
- `json_path`
- `output_format`
- `extraction_mode`
- `page_count`
- `extraction_status`
- `created_at`

**Validation Rules**:

- `markdown_path` e `json_path` devem apontar para artefatos produzidos pelo runtime oficial quando a extração for bem-sucedida.
- `output_format` deve suportar pelo menos a combinação que preserva texto legível e estrutura auditável.
- `extraction_status` deve suportar `generated`, `reused`, `invalidated`, `failed`.

### 3. WorkflowCheckpoint

**Purpose**: Representa um snapshot persistido do estado do workflow para pausa, retomada e auditoria.

**Fields**:

- `checkpoint_id`
- `job_id`
- `thread_id`
- `node_name`
- `checkpoint_status`
- `state_digest`
- `review_required`
- `created_at`
- `restored_at`

**Validation Rules**:

- Todo checkpoint deve pertencer a um `RuntimeIngestionJob`.
- `node_name` deve identificar unicamente o ponto do fluxo em que a pausa ou persistência ocorreu.
- `checkpoint_status` deve suportar `active`, `superseded`, `restored`, `completed`.

### 4. ReviewCase

**Purpose**: Representa um caso ambíguo encaminhado ao ramo assistido do workflow.

**Fields**:

- `review_case_id`
- `job_id`
- `entity_type`
- `entity_id`
- `ambiguity_reason`
- `confidence_snapshot`
- `ai_review_status`
- `human_review_status`
- `opened_at`
- `resolved_at`

**Validation Rules**:

- Todo `ReviewCase` deve apontar para uma entidade de negócio ou candidato rastreável.
- `confidence_snapshot` deve registrar o valor que motivou a abertura do caso.
- Pelo menos um entre `ai_review_status` e `human_review_status` deve existir enquanto o caso estiver aberto.

### 5. ReviewContextDocument

**Purpose**: Representa o documento estruturado fornecido ao agente de IA para revisão de ambiguidade.

**Fields**:

- `context_document_id`
- `review_case_id`
- `source_page`
- `content_format`
- `content_excerpt`
- `metadata_snapshot`
- `created_at`

**Validation Rules**:

- `content_format` deve refletir o formato realmente entregue ao ramo assistido.
- `metadata_snapshot` deve preservar referência de página e origem suficiente para auditoria.
- O conteúdo precisa continuar derivado do mesmo PDF que originou o `ReviewCase`.

### 6. ReviewResolution

**Purpose**: Representa a decisão final aplicada a um caso de revisão.

**Fields**:

- `resolution_id`
- `review_case_id`
- `resolution_source`
- `resolution_status`
- `resolution_summary`
- `resolved_payload_ref`
- `applied_at`

**Validation Rules**:

- `resolution_source` deve suportar `rule`, `ai_agent`, `human`.
- `resolution_status` deve suportar `accepted`, `rejected`, `edited`, `escalated`.
- Uma resolução aplicada deve ser suficiente para permitir retomada ou encerramento do workflow.

### 7. StructuredInvoiceResult

**Purpose**: Representa a consolidação das entidades canônicas já existentes após a execução do workflow oficial.

**Fields**:

- `job_id`
- `statement_ids`
- `transactions_persisted`
- `installment_plans_updated`
- `projections_updated`
- `review_items_opened`
- `result_status`

**Validation Rules**:

- `result_status` deve refletir o resultado observável da execução: `parsed`, `review_required`, `partial`, `failed`.
- Os contadores devem permanecer coerentes com as entidades realmente persistidas na base canônica.

## Relationships

- Um `RuntimeIngestionJob` produz zero ou um `ExtractedDocumentArtifact`.
- Um `RuntimeIngestionJob` pode produzir múltiplos `WorkflowCheckpoint`.
- Um `RuntimeIngestionJob` pode abrir múltiplos `ReviewCase`.
- Um `ReviewCase` pode referenciar múltiplos `ReviewContextDocument`.
- Um `ReviewCase` pode terminar em zero ou uma `ReviewResolution`.
- Um `RuntimeIngestionJob` termina em um `StructuredInvoiceResult`, que referencia entidades canônicas já existentes na solução.

## State Transitions

### RuntimeIngestionJob

- `initialized` → `extracting`
- `extracting` → `parsing`
- `parsing` → `awaiting_review`
- `parsing` → `persisting`
- `awaiting_review` → `persisting`
- `persisting` → `completed`
- `extracting|parsing|awaiting_review|persisting` → `failed`

### ReviewCase

- `open` → `ai_proposed`
- `open` → `human_required`
- `ai_proposed` → `accepted`
- `ai_proposed` → `edited`
- `human_required` → `accepted`
- `human_required` → `rejected`
- `human_required` → `edited`

### WorkflowCheckpoint

- `active` → `restored`
- `active` → `completed`
- `active` → `superseded`
