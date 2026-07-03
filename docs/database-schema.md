# Schema do Banco

Este projeto usa PostgreSQL e inicializa o schema em [src/faturama/infrastructure/database/schema.py](/Users/USER_PROFILE/Documents/faturama/src/faturama/infrastructure/database/schema.py:1).

## Visão geral

- Base transacional única:
  `FATURAMA_DB_DSN`, única fonte de configuração para dados canônicos, read models e checkpoints.
- O schema é criado por `initialize_schema(...)` ao conectar.
- Registros antigos fora do runtime oficial são marcados como `legacy_status='invalidated'` e ficam fora das consultas.

## Fluxo resumido

1. O PDF processado gera um registro em `documents`.
2. A fatura consolidada daquele documento gera um registro em `statements`.
3. Cada linha de compra/pagamento gera um registro em `transactions`.
4. Linhas parceladas geram ou atualizam `installment_plans` e `projections`.
5. A competência mensal agregada gera ou atualiza `summaries`.
6. Evidências textuais vão para `evidences`.
7. Decisões automáticas ou humanas vão para `decision_records`.
8. Casos pendentes de revisão vão para `review_items`.
9. O workflow do `LangGraph` persiste snapshots em `workflow_checkpoints`.

## Tabelas

### `documents`

Função:
Registrar a identidade do arquivo PDF processado e os artefatos brutos associados ao documento.

Uso operacional:

- escrita por `StatementRepository.save_document(...)`
- leitura por `StatementRepository.get_document_by_hash(...)`
- usada para idempotência via `file_hash`

Colunas-chave:

- `document_id`: identificador canônico do documento
- `file_hash`: hash SHA-256 do PDF, único
- `source_pdf_path`: caminho do PDF de origem
- `raw_markdown_path`, `raw_json_path`: artefatos gerados/reutilizados pelo runtime
- `runtime_source`: `official` ou `legacy`
- `legacy_status`: controla se o histórico pode ser consultado
- `partial_status`: indica se a ingestão ficou parcial

### `statements`

Função:
Representar a fatura já interpretada para uma competência e um cartão.

Uso operacional:

- escrita por `StatementRepository.save_statement(...)`
- leitura por `list_statements`, `get_statement` e `list_statements_filtered`
- usada como base para consultas por mês e cartão

Colunas-chave:

- `statement_id`: identificador da fatura
- `document_id`: documento de origem
- `card_fingerprint`: identidade estável do cartão
- `billing_year`, `billing_month`: competência da fatura
- `statement_status`: estado da fatura, como `parsed` ou `partial`
- `parse_confidence`: confiança estrutural geral
- `runtime_source`, `legacy_status`, `partial_status`: governança de validade operacional

### `evidences`

Função:
Guardar o trecho bruto extraído que sustenta uma linha ou decisão do pipeline.

Uso operacional:

- escrita por `EvidenceRepository.save_evidence(...)`
- vinculada a `transactions.source_evidence_id`

Colunas-chave:

- `evidence_id`: identificador da evidência
- `document_id`: documento de origem
- `raw_text`: trecho bruto observado
- `page_number`: página onde o trecho apareceu
- `extraction_method`: método usado para extrair
- `structural_confidence`: confiança da extração estrutural

### `transactions`

Função:
Persistir cada lançamento canônico da fatura, já classificado e com metadados de decisão.

Uso operacional:

- escrita por `TransactionRepository.save_transaction(...)`
- leitura por `list_by_statement`, `list_by_month` e `find_by_line_hash`
- base de consultas de compras, parcelas observadas e revisão

Colunas-chave:

- `transaction_id`: identificador da transação
- `statement_id`, `document_id`: vínculos de origem
- `line_hash`: chave estável da linha dentro da fatura
- `transaction_kind`: tipo operacional da linha
- `review_status`: situação da revisão
- `decision_state`: resultado da política de decisão
- `source_evidence_id`: evidência principal
- `source_strategy`: `rule`, `ai_agent` ou equivalente
- `is_installment`, `installment_current`, `installment_total`: semântica de parcelamento

Observação:

- há `UNIQUE(statement_id, line_hash)` para evitar duplicação no reprocessamento

### `installment_plans`

Função:
Consolidar uma compra parcelada como entidade de longo prazo, atravessando múltiplas faturas.

Uso operacional:

- escrita por `InstallmentRepository.save_plan(...)`
- leitura por `InstallmentRepository.list_plans(...)`
- usada para saldo restante e projeções futuras

Colunas-chave:

- `installment_plan_id`: identificador do plano parcelado
- `canonical_key`: chave única da compra parcelada
- `description_anchor`, `description_normalized`, `merchant_normalized`: identidade semântica do parcelamento
- `installment_amount`, `installment_total`: contrato financeiro do plano
- `first_seen_statement_id`, `last_seen_statement_id`: janela observada do plano
- `plan_status`, `plan_confidence`, `matching_strategy`: governança do matching
- `runtime_source`, `legacy_status`: validade operacional

### `projections`

Função:
Persistir as parcelas futuras projetadas de cada `installment_plan`.

Uso operacional:

- regravada por `InstallmentRepository.save_projections(...)`
- lida por `InstallmentRepository.list_projections(...)`
- usada por queries de parcelas futuras e saldo restante

Colunas-chave:

- `projection_id`: identificador da projeção
- `installment_plan_id`: plano ao qual pertence
- `projected_billing_year`, `projected_billing_month`: competência futura
- `projected_installment_number`: número da parcela projetada
- `projected_amount`: valor futuro esperado
- `projection_status`, `projection_confidence`: governança da projeção

Observação:

- há unicidade por plano + competência + número da parcela

### `summaries`

Função:
Materializar um read model mensal por cartão para consultas rápidas.

Uso operacional:

- escrita por `SummaryRepository.upsert_summary(...)`
- leitura por `SummaryRepository.list_summaries(...)`
- usada pela query `monthly_spend`

Colunas-chave:

- `summary_id`: identificador do resumo
- `user_id`, `card_fingerprint`, `billing_year`, `billing_month`: chave funcional do resumo
- `statement_total_amount`: total da fatura
- `new_purchase_total`: compras novas
- `installment_charge_total`: parcelas cobradas no mês
- `future_installment_balance`: saldo futuro total projetado
- `next_cycle_installment_commitment`: compromisso do próximo ciclo
- `runtime_source`, `legacy_status`: governança de validade

Observação:

- há `UNIQUE(user_id, card_fingerprint, billing_year, billing_month)`

### `review_items`

Função:
Representar pendências operacionais abertas para revisão humana.

Uso operacional:

- escrita por `ReviewRepository.save_review_item(...)`
- listada por `review-queue`
- resolvida por `ReviewRepository.resolve_review_item(...)`
- reutilizada no reprocessamento para não reabrir a mesma pendência resolvida

Colunas-chave:

- `review_item_id`: identificador da pendência
- `entity_type`, `entity_id`: entidade sob revisão
- `reason_code`, `reason_detail`: motivo da revisão
- `confidence_threshold_snapshot`: limiar usado na hora da decisão
- `severity`: severidade operacional
- `status`: `open` ou `resolved`
- `resolution_note`, `resolution_payload`: decisão humana persistida

### `decision_records`

Função:
Persistir a trilha auditável de decisões tomadas no pipeline.

Uso operacional:

- escrita por `DecisionRepository.save_decision(...)`
- leitura por `DecisionRepository.list_decisions(...)`
- cobre decisões de regra, agente e revisão reaplicada

Colunas-chave:

- `decision_id`: identificador da decisão
- `entity_type`, `entity_id`: alvo da decisão
- `decision_state`: estado final da decisão
- `confidence_structural`, `confidence_semantic`, `confidence_relational`, `confidence_operational`: dimensões de confiança
- `decision_reason`: justificativa textual
- `decision_source`: origem da decisão, como `rule`, `ai_agent` ou `human_review`
- `audit_payload`: JSON com evidências complementares

### `workflow_checkpoints`

Função:
Persistir snapshots do estado do workflow oficial executado com `LangGraph`.

Uso operacional:

- escrita por `PostgresCheckpointStore.save(...)`
- leitura por `PostgresCheckpointStore.latest(...)`
- atualização por `PostgresCheckpointStore.mark_restored(...)`
- também pode coexistir com o checkpointer oficial `PostgresSaver` do `LangGraph`

Colunas-chave:

- `checkpoint_id`: identificador do checkpoint
- `job_id`: execução de ingestão
- `thread_id`: thread lógica do workflow
- `node_name`: nó do workflow que gerou o snapshot
- `checkpoint_status`: estado do checkpoint
- `state_json`: payload serializado do estado completo
- `review_required`: flag para pausa operacional
- `created_at`, `restored_at`: trilha temporal

### `upload_authorization_grants`

Função:
Registrar as autorizações temporárias concedidas para upload de arquivos PDFs de fatura (por exemplo, via presigned URL do S3).

Uso operacional:
- escrita ao conceder autorização para upload
- leitura para confirmar se o upload foi completado dentro do tempo limite

Colunas-chave:
- `upload_grant_id`: identificador único da autorização
- `authorized_bucket`, `authorized_object_key`: destino autorizado no S3
- `granted_at`, `expires_at`: janela temporal de validade da autorização
- `upload_completed_at`: data/hora de confirmação do término do upload
- `grant_status`: status da autorização (ex: `pending`, `completed`, `expired`)

### `source_object_events`

Função:
Registrar e deduplicar os eventos de criação/modificação de objetos no S3 local ou AWS de produção.

Uso operacional:
- escrita ao receber um evento de webhook ou notificação do S3 (via EventBridge ou Lambda)
- chave única `dedupe_key` para evitar disparos duplicados do mesmo arquivo

Colunas-chave:
- `source_event_id`: identificador canônico do evento
- `bucket_name`, `object_key`: identificação do arquivo no S3
- `event_time`, `event_name`: data/hora e tipo do evento S3
- `dedupe_key`: string de deduplicação (geralmente baseada em bucket + key + etag)

### `processing_jobs`

Função:
Acompanhar a execução dos jobs assíncronos no ECS iniciados a partir de eventos do S3.

Uso operacional:
- escrita ao despachar o job ECS pela Lambda/EventBridge
- atualização periódica de status conforme o worker processa o arquivo

Colunas-chave:
- `processing_id`: identificador canônico da execução do job
- `source_event_id`: referência ao evento S3 que originou o processamento
- `current_status`: status atual do processamento (ex: `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`)
- `bucket_name`, `object_key`: arquivo sendo processado
- `requested_at`, `started_at`, `finished_at`: linha do tempo da execução

### `processing_lifecycle_events`

Função:
Manter um histórico cronológico auditável de todas as transições de status de cada job de processamento.

Uso operacional:
- escrita acionada em cada transição de status de processamento
- lida para auditar tempos de execução e gargalos

Colunas-chave:
- `event_id`: identificador do evento de ciclo de vida
- `processing_id`: job associado
- `event_name`, `status`: nome do evento e status de transição correspondente
- `payload_json`: detalhes e contexto adicional no formato JSON

### `artifact_manifests`

Função:
Registrar o manifesto final de todos os artefatos de saída gerados pela execução de um job de processamento de fatura e salvos no S3 de destino.

Uso operacional:
- escrita ao término bem-sucedido (ou parcial) do processamento do workflow
- leitura para retornar os links de download dos arquivos extraídos

Colunas-chave:
- `artifact_manifest_id`: identificador único do manifesto
- `processing_id`: job correspondente
- `source_pdf_uri`, `markdown_uri`, `json_uri`, `result_uri`: URIs completas no S3
- `artifact_key_prefix`: prefixo do caminho dos artefatos
- `checksum`: hash de integridade dos arquivos

### `processing_status_read_model`

Função:
Prover uma projeção de leitura simplificada para consultas instantâneas sobre o estado geral e resultado de qualquer processamento de fatura.

Uso operacional:
- escrita/atualização em tempo real conforme os jobs progridem ou mudam de fase
- lida diretamente por ferramentas de monitoramento e testes de integração

Colunas-chave:
- `processing_id`: identificador do processamento
- `current_status`: status do processamento
- `is_terminal`: booleano indicando se o job terminou (sucesso ou falha definitiva)
- `review_required`: booleano indicando se o workflow está travado aguardando revisão humana
- `last_transition_at`, `updated_at`: timestamps de controle temporal

## Relações lógicas

- `documents` 1:N `statements`
- `documents` 1:N `evidences`
- `statements` 1:N `transactions`
- `transactions` N:1 `evidences` via `source_evidence_id`
- `installment_plans` 1:N `projections`
- `transactions` e outras entidades 1:N `decision_records`
- `transactions` e outras entidades 1:N `review_items`
- `workflow_checkpoints` pertence a um `job_id`, não a uma entidade canônica

## Diagrama ER

```mermaid
erDiagram
    documents {
        TEXT document_id PK
        TEXT user_id
        TEXT file_hash UK
        TEXT source_pdf_path
        TEXT raw_markdown_path
        TEXT raw_json_path
        TEXT runtime_source
        TEXT legacy_status
        TEXT partial_status
    }

    statements {
        TEXT statement_id PK
        TEXT document_id
        TEXT user_id
        TEXT card_fingerprint
        INTEGER billing_year
        INTEGER billing_month
        TEXT statement_status
        REAL parse_confidence
        TEXT runtime_source
        TEXT legacy_status
        TEXT partial_status
    }

    evidences {
        TEXT evidence_id PK
        TEXT document_id
        INTEGER page_number
        TEXT raw_text
        TEXT extraction_method
        REAL structural_confidence
    }

    transactions {
        TEXT transaction_id PK
        TEXT statement_id
        TEXT document_id
        TEXT source_evidence_id
        TEXT card_fingerprint
        TEXT line_hash
        TEXT transaction_kind
        REAL parse_confidence
        TEXT review_status
        TEXT decision_state
        TEXT source_strategy
        BOOLEAN is_installment
        INTEGER installment_current
        INTEGER installment_total
    }

    installment_plans {
        TEXT installment_plan_id PK
        TEXT user_id
        TEXT card_fingerprint
        TEXT canonical_key UK
        TEXT description_anchor
        TEXT installment_amount
        INTEGER installment_total
        TEXT first_seen_statement_id
        TEXT last_seen_statement_id
        TEXT plan_status
        REAL plan_confidence
        TEXT runtime_source
        TEXT legacy_status
    }

    projections {
        TEXT projection_id PK
        TEXT installment_plan_id
        TEXT card_fingerprint
        INTEGER projected_billing_year
        INTEGER projected_billing_month
        INTEGER projected_installment_number
        TEXT projected_amount
        TEXT projection_status
        REAL projection_confidence
    }

    summaries {
        TEXT summary_id PK
        TEXT user_id
        TEXT card_fingerprint
        INTEGER billing_year
        INTEGER billing_month
        TEXT statement_total_amount
        TEXT new_purchase_total
        TEXT installment_charge_total
        TEXT future_installment_balance
        TEXT next_cycle_installment_commitment
        TEXT runtime_source
        TEXT legacy_status
    }

    review_items {
        TEXT review_item_id PK
        TEXT user_id
        TEXT entity_type
        TEXT entity_id
        TEXT reason_code
        TEXT severity
        TEXT status
        TEXT resolution_note
        TEXT resolution_payload
    }

    decision_records {
        TEXT decision_id PK
        TEXT entity_type
        TEXT entity_id
        TEXT decision_state
        REAL confidence_structural
        REAL confidence_semantic
        REAL confidence_relational
        REAL confidence_operational
        TEXT decision_reason
        TEXT decision_source
        TEXT audit_payload
    }

    workflow_checkpoints {
        TEXT checkpoint_id PK
        TEXT job_id
        TEXT thread_id
        TEXT node_name
        TEXT checkpoint_status
        TEXT state_json
        BOOLEAN review_required
        TEXT created_at
        TEXT restored_at
    }

    upload_authorization_grants {
        TEXT upload_grant_id PK
        TEXT authorized_bucket
        TEXT authorized_object_key
        TEXT granted_at
        TEXT expires_at
        TEXT upload_completed_at
        TEXT grant_status
    }

    source_object_events {
        TEXT source_event_id PK
        TEXT bucket_name
        TEXT object_key
        TEXT event_time
        TEXT event_name
        TEXT upload_grant_id
        TEXT dedupe_key UK
    }

    processing_jobs {
        TEXT processing_id PK
        TEXT source_event_id
        TEXT current_status
        TEXT bucket_name
        TEXT object_key
        TEXT document_id
        TEXT file_hash
        TEXT requested_at
        TEXT started_at
        TEXT finished_at
    }

    processing_lifecycle_events {
        TEXT event_id PK
        TEXT processing_id
        TEXT event_name
        TEXT status
        TEXT created_at
    }

    artifact_manifests {
        TEXT artifact_manifest_id PK
        TEXT processing_id UK
        TEXT artifact_bucket
        TEXT source_pdf_uri
        TEXT markdown_uri
        TEXT json_uri
        TEXT result_uri
        TEXT created_at
        TEXT updated_at
    }

    processing_status_read_model {
        TEXT processing_id PK
        TEXT document_id
        TEXT file_hash
        TEXT current_status
        BOOLEAN is_terminal
        BOOLEAN review_required
        TEXT last_transition_at
        TEXT updated_at
    }

    documents ||--o{ statements : origina
    documents ||--o{ evidences : produz
    documents ||--o{ transactions : contextualiza
    statements ||--o{ transactions : contem
    evidences ||--o{ transactions : sustenta
    statements ||--o{ installment_plans : observa
    installment_plans ||--o{ projections : projeta
    statements ||--o{ summaries : agrega
    transactions ||--o{ decision_records : registra
    transactions ||--o{ review_items : abre

    source_object_events ||--o| upload_authorization_grants : associa
    processing_jobs ||--o| source_object_events : origina
    processing_lifecycle_events }o--|| processing_jobs : loga
    artifact_manifests ||--|| processing_jobs : descreve
    processing_status_read_model ||--|| processing_jobs : projeta
```

## Regras importantes de negócio refletidas no schema

- `file_hash` em `documents` sustenta idempotência por PDF.
- `line_hash` em `transactions` evita duplicar linhas no reprocessamento.
- `canonical_key` em `installment_plans` evita duplicar o mesmo parcelamento entre ciclos.
- `legacy_status='invalidated'` bloqueia o uso operacional de dados antigos fora do runtime oficial.
- `partial_status` permite persistência auditável mesmo quando a ingestão não fechou 100%.

## Onde consultar no código

- schema: [src/faturama/infrastructure/database/schema.py](/Users/USER_PROFILE/Documents/faturama/src/faturama/infrastructure/database/schema.py:1)
- conexão PostgreSQL: [src/faturama/infrastructure/database/postgres.py](/Users/USER_PROFILE/Documents/faturama/src/faturama/infrastructure/database/postgres.py:1)
- repositórios: [src/faturama/infrastructure/repositories](/Users/USER_PROFILE/Documents/faturama/src/faturama/infrastructure/repositories)
- workflow oficial: [src/faturama/application/use_cases/process_invoice.py](/Users/USER_PROFILE/Documents/faturama/src/faturama/application/use_cases/process_invoice.py:1)
