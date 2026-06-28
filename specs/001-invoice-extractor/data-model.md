# Data Model: Extrator de Faturas Estruturadas

## Overview

O modelo da v1 separa quatro grupos de dados:

1. documento bruto e evidências de origem;
2. entidades canônicas observadas em faturas;
3. entidades derivadas para parcelamento e projeção;
4. estados operacionais de confiança, revisão e explicabilidade.

## Entities

### 1. RawDocument

**Purpose**: Representa o artefato PDF processado e os arquivos derivados produzidos pela extração base.

**Fields**:

- `document_id`
- `user_id`
- `source_pdf_path`
- `file_hash`
- `issuer_hint`
- `detected_issuer`
- `layout_family`
- `raw_markdown_path`
- `raw_json_path`
- `page_count`
- `extraction_version`
- `created_at`

**Validation Rules**:

- `file_hash` deve ser único por conteúdo de arquivo na base canônica.
- `source_pdf_path`, `raw_markdown_path` e `raw_json_path` devem referenciar artefatos existentes no momento da persistência.

### 2. SourceEvidence

**Purpose**: Representa a origem auditável de qualquer campo ou entidade extraída.

**Fields**:

- `evidence_id`
- `document_id`
- `page_number`
- `raw_text`
- `bbox`
- `json_node_ref`
- `extraction_method`
- `structural_confidence`
- `created_at`

**Validation Rules**:

- `extraction_method` deve ser um de `rule`, `llm` ou `hybrid`.
- `raw_text` não pode ser vazio quando a evidência sustenta entidade persistida.

### 3. InvoiceStatement

**Purpose**: Representa a fatura canônica por competência e cartão.

**Fields**:

- `statement_id`
- `document_id`
- `user_id`
- `issuer_name`
- `card_fingerprint`
- `card_label`
- `card_last4`
- `card_holder_name`
- `billing_year`
- `billing_month`
- `billing_cycle_label`
- `statement_issue_date`
- `statement_close_date`
- `statement_due_date`
- `statement_total_amount`
- `minimum_payment_amount`
- `credit_limit_amount`
- `currency`
- `statement_status`
- `parse_confidence`
- `created_at`
- `updated_at`

**Validation Rules**:

- `billing_year`, `billing_month` e `card_fingerprint` devem identificar unicamente uma fatura ativa por documento.
- `statement_status` deve refletir `parsed`, `partial` ou `review_required`.
- `parse_confidence` deve ficar entre `0.0` e `1.0`.

### 4. TransactionLine

**Purpose**: Representa a menor unidade financeira relevante extraída da fatura.

**Fields**:

- `transaction_id`
- `statement_id`
- `document_id`
- `card_fingerprint`
- `posted_date`
- `purchase_date`
- `description_raw`
- `description_normalized`
- `merchant_normalized`
- `amount`
- `currency`
- `transaction_kind`
- `is_installment`
- `installment_current`
- `installment_total`
- `line_hash`
- `source_strategy`
- `decision_state`
- `parse_confidence`
- `review_status`
- `created_at`
- `updated_at`

**Validation Rules**:

- `amount` deve ser valor monetário absoluto acompanhado por `transaction_kind` que explica o sinal operacional.
- `installment_current` e `installment_total` são obrigatórios para transações classificadas como `installment_charge` ou `invoice_installment`.
- `line_hash` deve ser estável sob reprocessamento do mesmo conteúdo.
- toda transação abaixo do limiar configurado de confiança deve receber `review_status` aberto para fila manual antes de qualquer aceitação final como canônica.

### 5. InstallmentPlan

**Purpose**: Representa uma compra parcelada consolidada ao longo de múltiplas competências.

**Fields**:

- `installment_plan_id`
- `user_id`
- `card_fingerprint`
- `installment_type`
- `description_anchor`
- `description_normalized`
- `merchant_normalized`
- `origin_purchase_date`
- `installment_amount`
- `installment_total`
- `first_seen_statement_id`
- `last_seen_statement_id`
- `plan_status`
- `plan_confidence`
- `matching_strategy`
- `canonical_key`
- `created_at`
- `updated_at`

**Validation Rules**:

- `installment_type` deve separar compra parcelada de parcelamento da própria fatura.
- `installment_total` deve ser maior que zero.
- `plan_status` deve ser um de `active`, `completed`, `uncertain`, `cancelled`.
- `canonical_key` deve ser derivável da combinação de descrição normalizada, valor da parcela, cartão e data de origem aproximada.

### 6. InstallmentOccurrence

**Purpose**: Representa a ligação entre uma transação observada e um plano parcelado.

**Fields**:

- `occurrence_id`
- `installment_plan_id`
- `transaction_id`
- `statement_id`
- `installment_number`
- `billing_year`
- `billing_month`
- `amount`
- `match_confidence`
- `created_at`

**Validation Rules**:

- `installment_number` não pode exceder `installment_total` do plano.
- Deve haver no máximo uma ocorrência por plano e número de parcela, salvo item retido para revisão.

### 7. FutureInstallmentProjection

**Purpose**: Representa uma parcela ainda não observada, prevista a partir de um plano parcelado ativo.

**Fields**:

- `projection_id`
- `installment_plan_id`
- `card_fingerprint`
- `projected_billing_year`
- `projected_billing_month`
- `projected_installment_number`
- `projected_amount`
- `projection_status`
- `projection_confidence`
- `created_at`
- `updated_at`

**Validation Rules**:

- `projected_installment_number` deve ser maior que a última parcela observada e menor ou igual ao total do plano.
- `projection_status` deve suportar pelo menos `projected`, `realized`, `superseded`, `cancelled`.

### 8. MonthlyCardSummary

**Purpose**: Representa o read model agregado por competência e cartão.

**Fields**:

- `summary_id`
- `user_id`
- `card_fingerprint`
- `issuer_name`
- `card_label`
- `billing_year`
- `billing_month`
- `statement_total_amount`
- `new_purchase_total`
- `installment_charge_total`
- `invoice_financing_total`
- `interest_and_fees_total`
- `refund_total`
- `future_installment_balance`
- `next_cycle_installment_commitment`
- `created_at`
- `updated_at`

**Validation Rules**:

- O resumo deve ser recalculável a partir das entidades base.
- Campos de totalização devem deixar observado e projetado semanticamente separados.

### 9. ReviewItem

**Purpose**: Representa um item pendente de decisão manual.

**Fields**:

- `review_item_id`
- `user_id`
- `entity_type`
- `entity_id`
- `reason_code`
- `reason_detail`
- `confidence_threshold_snapshot`
- `severity`
- `status`
- `opened_at`
- `resolved_at`
- `resolution_note`

**Validation Rules**:

- `status` deve suportar pelo menos `open`, `in_progress`, `resolved`, `dismissed`.
- Todo item deve apontar para uma entidade existente ou para um identificador provisório rastreável.
- Itens abertos por baixa confiança devem registrar o limiar aplicado no momento da decisão.

### 10. DecisionRecord

**Purpose**: Explica como o sistema aceitou, rejeitou, conciliou ou reteve uma entidade.

**Fields**:

- `decision_id`
- `entity_type`
- `entity_id`
- `decision_state`
- `confidence_structural`
- `confidence_semantic`
- `confidence_relational`
- `confidence_operational`
- `primary_evidence_source`
- `conflicting_sources`
- `decision_reason`
- `review_required`
- `created_at`

**Validation Rules**:

- Todas as confidências devem ficar entre `0.0` e `1.0`.
- `decision_state` deve suportar `accepted_high`, `accepted_medium`, `review_required`, `rejected`.

## Relationships

- `RawDocument 1:N SourceEvidence`
- `RawDocument 1:N InvoiceStatement`
- `InvoiceStatement 1:N TransactionLine`
- `TransactionLine N:N SourceEvidence` via tabela de vínculo de evidências por campo ou entidade
- `InstallmentPlan 1:N InstallmentOccurrence`
- `TransactionLine 0..1 -> InstallmentOccurrence`
- `InstallmentPlan 1:N FutureInstallmentProjection`
- `InvoiceStatement 1:1 MonthlyCardSummary` por cartão e competência
- `ReviewItem N:1` para qualquer entidade revisável
- `DecisionRecord N:1` para qualquer entidade decisória

## Derived Read Models

### monthly_card_summaries

Materialização usada para responder:

- total do mês por cartão;
- composição do gasto por categoria;
- saldo futuro agregado;
- comprometimento da próxima competência.

### installment_plan_snapshot

Materialização usada para responder:

- saldo restante por compra parcelada;
- próxima parcela prevista;
- status do plano;
- última ocorrência observada.

## State Transitions

### InvoiceStatement

- `parsed`: metadados e lançamentos essenciais extraídos sem bloqueio material.
- `partial`: resultado útil, mas com lacunas não impeditivas.
- `review_required`: existe ao menos um item abaixo do limiar configurado ou conflito material que exige fila manual.

### InstallmentPlan

- `active`: plano com ocorrências ou projeções futuras válidas.
- `completed`: última parcela observada ou projeções encerradas.
- `uncertain`: lacuna histórica ou conflito material impede fechamento seguro.
- `cancelled`: revisão ou evidência posterior indicou cancelamento.

### ReviewItem

- `open` -> `in_progress` -> `resolved`
- `open` -> `dismissed`

## Idempotency Strategy

- `RawDocument` deduplica por `file_hash`.
- `InvoiceStatement` deduplica por documento, cartão e competência.
- `TransactionLine` usa `line_hash` e reconciliação por evidência para impedir duplicação intra-fatura e interprocessamento.
- `FutureInstallmentProjection` é recalculada por plano e competência alvo, com substituição determinística do estado anterior.
