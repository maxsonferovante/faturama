# Schemas Pydantic v1 e Modelo Relacional/Canônico de Persistência

## Objetivo

Este documento fecha a arquitetura de dados da v1 do extrator de faturas. O foco aqui é definir, de forma funcional e técnica:

- quais entidades Pydantic compõem o pipeline;
- quais campos cada entidade precisa ter;
- como essas entidades se relacionam no modelo persistido;
- o que significa, na prática, uma `transação`, um `plano parcelado` e uma `projeção futura`.

Sem essa definição, o pipeline corre o risco de extrair muito texto útil, mas sem uma estrutura consistente para consulta, auditoria e evolução.

## Princípios de modelagem

### 1. A estrutura canônica não pode depender do layout do banco

O PDF de cada emissor muda, mas o modelo persistido precisa continuar estável. O layout do Inter, Itaú ou outro emissor influencia a extração, não a forma final dos dados.

### 2. A entidade principal não é a fatura, é a movimentação financeira vinculada a contexto

A fatura é o documento-fonte. O dado útil para consulta é:

- o cabeçalho da fatura;
- cada lançamento financeiro;
- os vínculos entre lançamentos parcelados;
- a projeção das parcelas futuras;
- os agregados por competência e cartão.

### 3. O modelo precisa ser auditável

Toda entidade financeira relevante deve manter vínculo com sua origem:

- arquivo;
- página;
- texto bruto;
- método de extração;
- confiança.

### 4. O modelo deve suportar reprocessamento idempotente

O mesmo PDF pode ser processado novamente, com regras melhores, sem duplicar entidades canônicas indevidamente.

### 5. A LLM não define a verdade canônica sozinha

Saídas inferidas por LLM devem entrar como dados estruturados com rastreabilidade e confiança, nunca como substituição opaca dos dados de origem.

## Conceitos centrais

### O que é `transação`

Na v1, `transação` é a menor unidade financeira relevante extraída de uma fatura que represente um lançamento com significado contábil ou analítico.

Exemplos:

- compra nova;
- parcela cobrada no mês;
- estorno;
- pagamento;
- juros;
- ajuste;
- parcelamento da própria fatura.

Não são transações:

- textos promocionais;
- instruções de pagamento;
- blocos de contrato;
- explicações de limite;
- mensagens genéricas do emissor.

### O que é `plano parcelado`

`Plano parcelado` é a entidade que representa uma compra parcelada como objeto histórico único, independente de quantas faturas ela apareça.

Ele não representa uma parcela isolada. Ele representa o vínculo entre:

- a compra original;
- a quantidade total de parcelas;
- o valor recorrente;
- o cartão em que ocorreu;
- o conjunto de cobranças mensais associadas.

Exemplos:

- `Mercado Livre, 10 parcelas de R$ 422,89`;
- `Beto Carrero, 10 parcelas de R$ 101,96`.

### O que é `projeção futura`

`Projeção futura` é a expectativa estruturada de uma parcela ainda não cobrada, derivada de um plano parcelado conhecido.

Ela existe para responder consultas como:

- quais parcelas terei no próximo mês;
- quanto do meu cartão já está comprometido nas próximas competências;
- quanto ainda falta quitar de uma compra parcelada.

Uma projeção não é uma transação real já ocorrida. É uma previsão derivada do plano parcelado.

## Camadas de schema

A proposta é separar os modelos Pydantic em 4 camadas:

1. entrada do workflow;
2. extração intermediária;
3. modelo canônico persistível;
4. modelos de consulta e agregação.

## 1. Schemas de entrada do workflow

### `InvoiceInput`

Representa a entrada mínima para processamento de um documento.

Campos sugeridos:

- `job_id: str`
- `user_id: str`
- `pdf_path: str`
- `issuer_hint: str | None`
- `currency: str = "BRL"`
- `locale: str = "pt-BR"`
- `timezone: str`
- `document_type: Literal["credit_card_invoice"]`

### `ProcessingConfig`

Representa parâmetros operacionais do pipeline.

Campos sugeridos:

- `low_confidence_threshold: float`
- `enable_llm_fallback: bool`
- `enable_human_review: bool`
- `issuer_strategy_override: str | None`
- `allow_partial_header: bool`
- `projection_horizon_months: int`

## 2. Schemas de extração intermediária

### `RawInvoiceDocument`

Representa o documento bruto já extraído.

Campos sugeridos:

- `document_id: str`
- `file_hash: str`
- `source_pdf_path: str`
- `raw_markdown_path: str`
- `raw_json_path: str`
- `page_count: int`
- `issuer_detected: str | None`
- `layout_family: str | None`
- `extraction_version: str`

### `SourceEvidence`

Representa a evidência de origem de um dado extraído.

Campos sugeridos:

- `source_file: str`
- `page_number: int | None`
- `raw_text: str`
- `bbox: tuple[float, float, float, float] | None`
- `json_node_id: str | int | None`
- `extraction_method: Literal["rule", "llm", "hybrid"]`
- `confidence: float`

### `InvoiceHeader`

Representa o cabeçalho financeiro da fatura.

Campos sugeridos:

- `issuer_name: str | None`
- `card_label: str | None`
- `card_last4: str | None`
- `card_holder_name: str | None`
- `statement_due_date: date | None`
- `statement_close_date: date | None`
- `statement_issue_date: date | None`
- `next_close_date: date | None`
- `currency: str`
- `statement_total_amount: Decimal | None`
- `minimum_payment_amount: Decimal | None`
- `credit_limit_amount: Decimal | None`
- `previous_balance_amount: Decimal | None`
- `payments_amount: Decimal | None`
- `current_charges_amount: Decimal | None`
- `header_confidence: float`
- `evidence: list[SourceEvidence]`

### `TransactionCandidate`

Representa uma linha candidata a lançamento financeiro antes da estruturação completa.

Campos sugeridos:

- `candidate_id: str`
- `statement_id: str`
- `raw_text: str`
- `section_name: str | None`
- `page_number: int | None`
- `line_date_text: str | None`
- `amount_text: str | None`
- `candidate_confidence: float`
- `evidence: list[SourceEvidence]`

## 3. Schemas canônicos persistíveis

### `InvoiceStatement`

Representa a fatura como documento financeiro canônico.

Campos sugeridos:

- `statement_id: str`
- `document_id: str`
- `user_id: str`
- `issuer_name: str | None`
- `card_fingerprint: str`
- `card_label: str | None`
- `card_last4: str | None`
- `billing_year: int`
- `billing_month: int`
- `billing_cycle_label: str`
- `statement_due_date: date | None`
- `statement_close_date: date | None`
- `statement_issue_date: date | None`
- `currency: str`
- `statement_total_amount: Decimal | None`
- `minimum_payment_amount: Decimal | None`
- `credit_limit_amount: Decimal | None`
- `statement_status: Literal["parsed", "partial", "review_required"]`
- `parse_confidence: float`
- `created_at: datetime`
- `updated_at: datetime`

### `TransactionKind`

Enum lógico sugerido:

- `new_purchase`
- `installment_charge`
- `invoice_installment`
- `payment`
- `refund`
- `adjustment`
- `interest_fee`
- `tax_fee`
- `cash_withdrawal`
- `ignored_non_transaction`

### `TransactionLine`

Representa a unidade canônica de lançamento financeiro.

Campos sugeridos:

- `transaction_id: str`
- `statement_id: str`
- `user_id: str`
- `card_fingerprint: str`
- `transaction_kind: TransactionKind`
- `posted_date: date | None`
- `purchase_date: date | None`
- `merchant_raw: str`
- `merchant_normalized: str | None`
- `description_raw: str`
- `description_normalized: str | None`
- `amount: Decimal`
- `currency: str`
- `is_credit: bool`
- `is_debit: bool`
- `is_installment: bool`
- `installment_current: int | None`
- `installment_total: int | None`
- `installment_plan_id: str | None`
- `origin_channel: str | None`
- `category_hint: str | None`
- `line_hash: str`
- `parse_confidence: float`
- `review_status: Literal["accepted", "needs_review", "rejected"]`
- `created_at: datetime`
- `updated_at: datetime`

### `InstallmentPlan`

Representa a compra parcelada como entidade histórica única.

Campos sugeridos:

- `installment_plan_id: str`
- `user_id: str`
- `card_fingerprint: str`
- `issuer_name: str | None`
- `merchant_normalized: str | None`
- `description_anchor: str`
- `purchase_date_anchor: date | None`
- `first_seen_statement_id: str`
- `installment_total: int`
- `installment_amount: Decimal`
- `currency: str`
- `principal_estimated_amount: Decimal | None`
- `installment_type: Literal["merchant_purchase", "invoice_financing"]`
- `matching_strategy: Literal["exact_rule", "heuristic", "llm_assisted"]`
- `plan_confidence: float`
- `plan_status: Literal["active", "completed", "uncertain", "cancelled"]`
- `created_at: datetime`
- `updated_at: datetime`

### `InstallmentOccurrence`

Representa a ocorrência de uma parcela efetivamente cobrada em uma fatura.

Campos sugeridos:

- `occurrence_id: str`
- `installment_plan_id: str`
- `transaction_id: str`
- `statement_id: str`
- `installment_number: int`
- `amount: Decimal`
- `currency: str`
- `billing_year: int`
- `billing_month: int`
- `created_at: datetime`

### `FutureInstallmentProjection`

Representa uma parcela futura ainda não cobrada, derivada de um plano.

Campos sugeridos:

- `projection_id: str`
- `installment_plan_id: str`
- `user_id: str`
- `card_fingerprint: str`
- `projected_billing_year: int`
- `projected_billing_month: int`
- `projected_installment_number: int`
- `projected_amount: Decimal`
- `currency: str`
- `projection_status: Literal["projected", "realized", "superseded", "cancelled"]`
- `projection_confidence: float`
- `generated_from_statement_id: str`
- `created_at: datetime`
- `updated_at: datetime`

### `ReviewItem`

Representa uma pendência que exige revisão manual.

Campos sugeridos:

- `review_item_id: str`
- `entity_type: Literal["statement", "transaction", "installment_plan", "projection"]`
- `entity_id: str`
- `reason_code: str`
- `reason_detail: str`
- `severity: Literal["low", "medium", "high"]`
- `status: Literal["open", "resolved", "dismissed"]`
- `created_at: datetime`
- `resolved_at: datetime | None`

## 4. Schemas de consulta e agregação

### `MonthlyCardSummary`

Representa uma visão consolidada por cartão e competência.

Campos sugeridos:

- `summary_id: str`
- `user_id: str`
- `card_fingerprint: str`
- `issuer_name: str | None`
- `billing_year: int`
- `billing_month: int`
- `currency: str`
- `new_purchase_total: Decimal`
- `installment_charge_total: Decimal`
- `invoice_financing_total: Decimal`
- `refund_total: Decimal`
- `interest_and_fees_total: Decimal`
- `statement_total_amount: Decimal | None`
- `future_installment_balance: Decimal | None`
- `next_month_projected_installments: Decimal | None`
- `created_at: datetime`
- `updated_at: datetime`

### `InstallmentPlanSnapshot`

Representa uma visão consultável do plano parcelado.

Campos sugeridos:

- `installment_plan_id: str`
- `card_fingerprint: str`
- `description_anchor: str`
- `installment_total: int`
- `last_billed_installment_number: int | None`
- `remaining_installments_count: int`
- `remaining_balance_amount: Decimal`
- `next_projected_installment_amount: Decimal | None`
- `next_projected_billing_year: int | None`
- `next_projected_billing_month: int | None`
- `plan_status: str`

## Modelo relacional/canônico de persistência

## Objetivo do modelo relacional

O banco persistido deve servir para 4 coisas ao mesmo tempo:

1. guardar a origem bruta do processamento;
2. guardar a estrutura canônica consolidada;
3. permitir consultas analíticas simples;
4. permitir reprocessamento e auditoria.

## Tabelas principais

### 1. `documents`

Guarda o documento bruto e os artefatos de extração.

Campos principais:

- `document_id`
- `user_id`
- `source_pdf_path`
- `file_hash`
- `raw_markdown_path`
- `raw_json_path`
- `page_count`
- `issuer_detected`
- `layout_family`
- `extraction_version`
- `created_at`

### 2. `statements`

Guarda a fatura canônica.

Campos principais:

- `statement_id`
- `document_id`
- `user_id`
- `card_fingerprint`
- `issuer_name`
- `card_label`
- `card_last4`
- `billing_year`
- `billing_month`
- `billing_cycle_label`
- `statement_due_date`
- `statement_close_date`
- `statement_issue_date`
- `currency`
- `statement_total_amount`
- `minimum_payment_amount`
- `credit_limit_amount`
- `statement_status`
- `parse_confidence`
- `created_at`
- `updated_at`

### 3. `source_evidences`

Guarda a rastreabilidade granular da origem.

Campos principais:

- `evidence_id`
- `document_id`
- `statement_id | null`
- `transaction_id | null`
- `installment_plan_id | null`
- `projection_id | null`
- `source_file`
- `page_number`
- `raw_text`
- `bbox_json`
- `json_node_id`
- `extraction_method`
- `confidence`
- `created_at`

### 4. `transactions`

Guarda cada lançamento financeiro canônico.

Campos principais:

- `transaction_id`
- `statement_id`
- `user_id`
- `card_fingerprint`
- `transaction_kind`
- `posted_date`
- `purchase_date`
- `merchant_raw`
- `merchant_normalized`
- `description_raw`
- `description_normalized`
- `amount`
- `currency`
- `is_credit`
- `is_debit`
- `is_installment`
- `installment_current`
- `installment_total`
- `installment_plan_id | null`
- `origin_channel`
- `category_hint`
- `line_hash`
- `parse_confidence`
- `review_status`
- `created_at`
- `updated_at`

### 5. `installment_plans`

Guarda a compra parcelada como entidade única.

Campos principais:

- `installment_plan_id`
- `user_id`
- `card_fingerprint`
- `issuer_name`
- `merchant_normalized`
- `description_anchor`
- `purchase_date_anchor`
- `first_seen_statement_id`
- `installment_total`
- `installment_amount`
- `currency`
- `principal_estimated_amount`
- `installment_type`
- `matching_strategy`
- `plan_confidence`
- `plan_status`
- `created_at`
- `updated_at`

### 6. `installment_occurrences`

Guarda a ligação entre a parcela real cobrada e o plano parcelado.

Campos principais:

- `occurrence_id`
- `installment_plan_id`
- `transaction_id`
- `statement_id`
- `installment_number`
- `amount`
- `currency`
- `billing_year`
- `billing_month`
- `created_at`

### 7. `future_installment_projections`

Guarda as parcelas futuras previstas.

Campos principais:

- `projection_id`
- `installment_plan_id`
- `user_id`
- `card_fingerprint`
- `projected_billing_year`
- `projected_billing_month`
- `projected_installment_number`
- `projected_amount`
- `currency`
- `projection_status`
- `projection_confidence`
- `generated_from_statement_id`
- `created_at`
- `updated_at`

### 8. `review_items`

Guarda pendências de revisão.

Campos principais:

- `review_item_id`
- `entity_type`
- `entity_id`
- `reason_code`
- `reason_detail`
- `severity`
- `status`
- `created_at`
- `resolved_at`

### 9. `monthly_card_summaries`

Guarda agregados já prontos para consulta.

Campos principais:

- `summary_id`
- `user_id`
- `card_fingerprint`
- `issuer_name`
- `billing_year`
- `billing_month`
- `currency`
- `new_purchase_total`
- `installment_charge_total`
- `invoice_financing_total`
- `refund_total`
- `interest_and_fees_total`
- `statement_total_amount`
- `future_installment_balance`
- `next_month_projected_installments`
- `created_at`
- `updated_at`

## Relações principais

As relações canônicas são:

- `documents 1:N statements`
- `statements 1:N transactions`
- `transactions N:1 installment_plans` quando a transação for parcela
- `installment_plans 1:N installment_occurrences`
- `installment_plans 1:N future_installment_projections`
- `statements 1:N review_items`
- `transactions 1:N source_evidences`
- `installment_plans 1:N source_evidences`

## Chaves e identidade canônica

## Identidade do documento

`documents.file_hash` deve ser a chave lógica de idempotência do PDF bruto.

## Identidade da fatura

A identidade lógica da fatura pode ser derivada de:

- `user_id`
- `card_fingerprint`
- `billing_year`
- `billing_month`
- `statement_due_date`

## Identidade da transação

A identidade física pode ser `transaction_id`, mas a deduplicação deve considerar uma chave lógica baseada em:

- `statement_id`
- `posted_date | purchase_date`
- `amount`
- `description_raw`
- `page_number`
- `line_hash`

## Identidade do plano parcelado

O ponto mais sensível da modelagem é o `InstallmentPlan`.

A chave lógica sugerida deve considerar:

- `user_id`
- `card_fingerprint`
- `description_anchor` ou `merchant_normalized`
- `installment_total`
- `installment_amount`
- `purchase_date_anchor` aproximada

Essa chave não precisa ser pública, mas deve orientar o matching.

## Regras de modelagem importantes

### 1. Compra parcelada e parcelamento de fatura não são a mesma coisa

Essas duas entidades precisam ficar separadas por `installment_type`.

- `merchant_purchase`: compra parcelada no lojista;
- `invoice_financing`: parcelamento da própria fatura.

Misturar esses dois conceitos quebra quase todas as consultas futuras.

### 2. Projeção futura não substitui ocorrência real

Quando a parcela futura aparecer de fato numa fatura posterior:

- a projeção pode virar `realized`;
- a ocorrência real entra em `installment_occurrences`;
- a transação real continua sendo a verdade observada.

### 3. A transação pode existir sem plano parcelado

Nem toda transação parcelada precisa entrar imediatamente num plano com confiança alta. Em caso de dúvida:

- persistir a transação;
- marcar `is_installment = true`;
- deixar `installment_plan_id = null`;
- criar `review_item` se necessário.

### 4. A evidência não deve ficar apenas em logs

`SourceEvidence` precisa ser entidade persistida, não detalhe descartável.

## Consultas que esse modelo precisa suportar

Com esse desenho, as consultas principais ficam naturais:

### Parcelas do mês

Buscar em `transactions` onde:

- `transaction_kind = installment_charge`
- `billing_year` e `billing_month` da fatura desejada.

### Parcelas do próximo mês

Buscar em `future_installment_projections` onde:

- `projected_billing_year` e `projected_billing_month` desejados;
- `projection_status = projected`.

### Compras novas do mês

Buscar em `transactions` onde:

- `transaction_kind = new_purchase`.

### Gasto total do mês por cartão

Usar `monthly_card_summaries` ou agregar `transactions` por:

- `card_fingerprint`
- `billing_year`
- `billing_month`.

### Total parcelado futuro por cartão

Somar `projected_amount` em `future_installment_projections` por:

- `card_fingerprint`
- `projection_status = projected`.

### Saldo restante de cada compra parcelada

Usar `installment_plans` combinado com:

- `installment_occurrences`;
- `future_installment_projections`.

## Banco recomendado para a v1

Para a primeira versão, `SQLite` é suficiente e tem vantagens claras:

- simples para prototipar;
- ótimo para inspeção local;
- funciona bem com poucas tabelas relacionais;
- suficiente para consultas mensais e históricas do caso de uso.

Se depois houver necessidade analítica maior, o modelo pode migrar para:

- `Postgres`, se a prioridade for API multiusuário e integridade relacional;
- `DuckDB`, se a prioridade for análise local e consultas analíticas pesadas.

## Decisões fechadas por este refinamento

Este refinamento fecha as seguintes decisões arquiteturais:

1. `Transação` é a unidade financeira canônica mínima persistida.
2. `Plano parcelado` é a entidade histórica que agrupa parcelas da mesma compra.
3. `Projeção futura` é previsão derivada do plano parcelado, e não lançamento real.
4. `SourceEvidence` é parte obrigatória do modelo persistido.
5. `Compra parcelada` e `parcelamento de fatura` são categorias distintas.
6. O modelo final deve ser estável apesar das diferenças de layout entre bancos.

## Próximo passo lógico

O próximo passo, ainda sem implementar, seria escrever um documento complementar com:

- enums fechados da v1;
- regras de matching para `InstallmentPlan`;
- regras de deduplicação de `TransactionLine`;
- critérios de confiança e gatilhos de revisão manual.
