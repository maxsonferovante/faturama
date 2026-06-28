# Read Model Contract: Extrator de Faturas Estruturadas

## Purpose

Definir os contratos lógicos de leitura sustentados pela base canônica e consumidos pela CLI da v1.

## Query 1: Statements

**Inputs**:

- `user_id`
- `card_fingerprint?`
- `competency_range?`

**Output fields**:

- `statement_id`
- `issuer_name`
- `card_label`
- `card_last4`
- `billing_year`
- `billing_month`
- `statement_due_date`
- `statement_total_amount`
- `statement_status`
- `parse_confidence`

## Query 2: Statement Transactions

**Inputs**:

- `statement_id`
- `transaction_kind?`
- `is_installment?`
- `review_status?`

**Output fields**:

- `transaction_id`
- `posted_date`
- `purchase_date`
- `description_raw`
- `description_normalized`
- `merchant_normalized`
- `amount`
- `transaction_kind`
- `is_installment`
- `installment_current`
- `installment_total`
- `installment_plan_id`
- `parse_confidence`
- `review_status`
- `decision_state`

## Query 3: Monthly Spend by Card

**Inputs**:

- `user_id`
- `billing_year`
- `billing_month`
- `card_fingerprint?`

**Output fields**:

- `card_fingerprint`
- `issuer_name`
- `card_label`
- `statement_total_amount`
- `new_purchase_total`
- `installment_charge_total`
- `invoice_financing_total`
- `interest_and_fees_total`

## Query 4: Current Installments

**Inputs**:

- `user_id`
- `billing_year`
- `billing_month`
- `card_fingerprint?`

**Output fields**:

- `transaction_id`
- `card_fingerprint`
- `description_anchor`
- `installment_current`
- `installment_total`
- `amount`
- `installment_plan_id`
- `plan_status`

## Query 5: Future Installments

**Inputs**:

- `user_id`
- `projected_billing_year`
- `projected_billing_month`
- `card_fingerprint?`

**Output fields**:

- `projection_id`
- `card_fingerprint`
- `installment_plan_id`
- `description_anchor`
- `projected_installment_number`
- `installment_total`
- `projected_amount`
- `projection_confidence`
- `projection_status`

## Query 6: Remaining Installment Balance

**Inputs**:

- `user_id`
- `card_fingerprint?`
- `installment_plan_id?`

**Output fields**:

- `installment_plan_id`
- `card_fingerprint`
- `description_anchor`
- `installment_total`
- `installment_amount`
- `last_observed_installment`
- `remaining_installments`
- `remaining_balance`
- `next_projected_installment`
- `plan_status`
- `plan_confidence`

## Query 7: Review Queue

**Inputs**:

- `user_id`
- `entity_type?`
- `severity?`
- `status?`

**Output fields**:

- `review_item_id`
- `entity_type`
- `entity_id`
- `reason_code`
- `reason_detail`
- `severity`
- `status`
- `opened_at`

## Query 8: Decision Trace

**Inputs**:

- `entity_type`
- `entity_id`

**Output fields**:

- `decision_state`
- `confidence_structural`
- `confidence_semantic`
- `confidence_relational`
- `confidence_operational`
- `primary_evidence_source`
- `conflicting_sources`
- `decision_reason`
- `review_required`

## Semantics

- Consultas sobre gasto mensal usam somente dados observados.
- Consultas sobre competências futuras usam somente projeções.
- Parcelamento de compra e parcelamento da própria fatura permanecem separados por contrato.
- Resultados com pendência operacional devem expor status de revisão ou confiança quando isso alterar a interpretação da resposta.
- Todo item abaixo do limiar configurado deve aparecer como pendente de revisão até resolução manual explícita.
