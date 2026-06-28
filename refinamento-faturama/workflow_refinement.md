# Workflow de Extração e Estruturação de Faturas

## Visão geral

A proposta é modelar o processo com `LangGraph` como um workflow orquestrado de documento, e não como um agente livre lendo a fatura inteira.

O fluxo fica dividido em 3 blocos:

1. ingestão e leitura estrutural;
2. extração e reconciliação financeira;
3. projeção, persistência e revisão.

A ideia central é:

- `OpenDataLoader PDF` faz a extração base do PDF para `json` e `markdown`;
- regras determinísticas fazem a maior parte da estruturação;
- a LLM entra apenas como fallback controlado para ambiguidade;
- `LangGraph` coordena estado, checkpoints, retries e revisão humana;
- `Pydantic` valida todas as entradas e saídas relevantes.

## Princípio arquitetural

Este caso não pede um agente geral tomando decisões abertas a cada passo. O melhor desenho é um grafo com nós pequenos, previsíveis, auditáveis e com contratos de dados explícitos.

O papel da LLM deve ser restrito a:

- classificar linhas ambíguas;
- extrair campos de linhas mal formadas;
- normalizar descrições de lojista;
- ajudar em matching histórico quando a heurística falhar.

Todo o restante deve ser feito, preferencialmente, por extração estrutural e regras determinísticas.

## Estado do grafo

O estado compartilhado pode conter:

- `job_id`
- `user_id`
- `pdf_path`
- `issuer_hint | None`
- `raw_markdown_path | None`
- `raw_json_path | None`
- `raw_document | None`
- `invoice_statement | None`
- `candidate_lines`
- `structured_transactions`
- `installment_candidates`
- `installment_plans`
- `future_projections`
- `validation_errors`
- `review_queue`
- `processing_metrics`
- `status`

Separação recomendada:

- `GraphInput`: entrada inicial do processamento;
- `GraphState`: estado evolutivo interno do workflow.

## Nós do workflow

### 1. `ingest_document`

**Entrada**

- caminho do PDF.

**Função**

- registrar o job;
- gerar ids de processamento;
- validar se o arquivo existe;
- calcular hash do PDF.

**Saída**

- metadados básicos do job.

**Observação**

- o hash do arquivo é essencial para idempotência.

### 2. `extract_with_opendataloader`

**Entrada**

- PDF original.

**Função**

- chamar `opendataloader-pdf`;
- gerar artefatos `markdown` e `json`.

**Saída**

- `RawInvoiceDocument`.

**Observação**

- este nó não usa LLM.

### 3. `load_extracted_artifacts`

**Entrada**

- paths dos artefatos gerados.

**Função**

- carregar o JSON estruturado;
- carregar o markdown;
- montar uma representação unificada do documento.

**Saída**

- documento bruto unificado em memória.

**Observação**

- o `json` deve ser a fonte principal;
- o `markdown` serve como apoio contextual.

### 4. `detect_issuer_and_layout`

**Entrada**

- documento bruto.

**Função**

- inferir emissor;
- inferir família de layout;
- escolher estratégia de parsing.

**Saída**

- `issuer`;
- `layout_family`;
- `confidence`.

**Observação**

- isso permite ter parsers específicos por banco no futuro.

### 5. `extract_invoice_header`

**Entrada**

- documento bruto.

**Função**

- extrair vencimento;
- extrair fechamento;
- extrair emissão;
- extrair total da fatura;
- extrair pagamento mínimo;
- extrair limite;
- extrair nome do cartão;
- extrair final do cartão;
- extrair titular.

**Saída**

- `InvoiceStatement` parcial.

**Observação**

- este nó deve ser majoritariamente determinístico.

### 6. `segment_document_sections`

**Entrada**

- documento bruto.

**Função**

- dividir o documento em seções semânticas.

**Seções típicas**

- resumo da fatura;
- despesas da fatura;
- compras parceladas;
- próxima fatura;
- pagamentos e encargos;
- blocos promocionais.

**Saída**

- mapa de seções com evidência de origem.

**Observação**

- este nó melhora muito a precisão dos próximos.

### 7. `extract_transaction_candidates`

**Entrada**

- seções relevantes do documento.

**Função**

- localizar todas as linhas que parecem lançamentos financeiros.

**Saída**

- lista de `TransactionCandidate`.

**Observação**

- aqui vale capturar demais e filtrar depois;
- perder linha relevante é pior do que ter ruído temporário.

### 8. `parse_transactions_rule_based`

**Entrada**

- candidatos a transação.

**Função**

- aplicar regex;
- interpretar datas;
- interpretar valores monetários;
- detectar sinal positivo ou negativo;
- detectar padrões como `Parcela X de Y`.

**Saída**

- lista de `TransactionLine` com `confidence`.

**Observação**

- esta é a etapa principal da extração financeira.

### 9. `classify_transaction_kind`

**Entrada**

- transações estruturadas.

**Função**

- classificar cada item em tipos financeiros.

**Tipos sugeridos**

- `new_purchase`
- `installment_charge`
- `invoice_installment`
- `payment`
- `interest_fee`
- `refund`
- `adjustment`
- `ignored_non_transaction`

**Saída**

- transações classificadas.

**Observação**

- primeiro por regra;
- só usar LLM depois, para casos ambíguos.

### 10. `llm_disambiguation_fallback`

**Entrada**

- apenas itens ambíguos ou inválidos.

**Função**

- usar LLM com saída estruturada via Pydantic para:
- classificar linha duvidosa;
- extrair descrição, data, valor e tipo;
- sugerir descrição normalizada.

**Saída**

- correções estruturadas e validadas.

**Observação**

- este nó deve ser pequeno, barato e restrito.

### 11. `validate_and_reconcile_transactions`

**Entrada**

- resultados por regra;
- resultados do fallback LLM.

**Função**

- validar schema;
- remover duplicatas internas;
- reconciliar conflitos;
- consolidar a lista final de transações.

**Saída**

- `structured_transactions`.

**Observação**

- se regra e LLM divergirem, a decisão pode priorizar a origem com maior confiança.

### 12. `build_installment_candidates`

**Entrada**

- transações finais.

**Função**

- separar tudo que parece compra parcelada ou parcela recorrente.

**Saída**

- `installment_candidates`.

### 13. `group_installment_plans`

**Entrada**

- candidatos a parcelamento.

**Função**

- agrupar ocorrências mensais da mesma compra parcelada.

**Saída**

- `InstallmentPlan`.

**Chave canônica sugerida**

- cartão;
- descrição normalizada;
- valor da parcela;
- data de origem aproximada;
- total de parcelas.

**Observação**

- este é um dos nós mais importantes do sistema.

### 14. `project_future_installments`

**Entrada**

- planos parcelados.

**Função**

- gerar parcelas futuras por competência.

**Saída**

- `FutureInstallmentProjection`.

**Observação**

- este nó responde perguntas como:
- quais parcelas tenho no próximo mês;
- quanto ainda falta pagar por cartão;
- qual parte da próxima fatura já está comprometida.

### 15. `compute_monthly_summaries`

**Entrada**

- fatura;
- transações;
- projeções futuras.

**Função**

- gerar agregados por mês e cartão.

**Agregados sugeridos**

- total do mês por cartão;
- total de compras novas;
- total de parcelas cobradas;
- saldo parcelado futuro;
- próxima fatura estimada com base nas parcelas já conhecidas.

**Saída**

- `MonthlyCardSummary`.

### 16. `quality_gate`

**Entrada**

- entidades estruturadas produzidas pelo pipeline.

**Função**

- aplicar regras de qualidade.

**Checagens sugeridas**

- campos obrigatórios ausentes;
- confiança baixa;
- soma inconsistente com total da fatura;
- transações sem data;
- parcelas impossíveis;
- número de parcela maior que o total.

**Saída**

- decisão de seguir;
- encaminhar para revisão;
- ou falhar com erro explícito.

### 17. `human_review_queue`

**Entrada**

- itens problemáticos.

**Função**

- registrar casos para revisão manual.

**Saída**

- fila de revisão.

**Observação**

- este branch é um dos principais motivos para usar `LangGraph` com checkpoint.

### 18. `persist_canonical_data`

**Entrada**

- entidades validadas.

**Função**

- persistir documento bruto;
- persistir transações;
- persistir planos parcelados;
- persistir projeções;
- persistir sumários;
- persistir evidências de origem.

**Saída**

- ids persistidos;
- confirmação de gravação.

**Observação**

- `SQLite` já atende bem a primeira versão.

### 19. `emit_processing_report`

**Entrada**

- estado final do processamento.

**Função**

- gerar relatório técnico do job.

**Métricas sugeridas**

- quantas linhas foram extraídas;
- quantas foram resolvidas por regra;
- quantas exigiram LLM;
- quantas foram para revisão;
- confiança média;
- inconsistências detectadas.

**Saída**

- `ProcessingReport`.

## Branches condicionais do grafo

Os principais ramos condicionais recomendados são:

- se o emissor for reconhecido, usar parser e heurísticas específicas do layout;
- se o parser por regra falhar ou tiver baixa confiança, encaminhar apenas esses itens para `llm_disambiguation_fallback`;
- se a qualidade final ficar abaixo do limiar, seguir para `human_review_queue`;
- se o hash do documento já existir, ativar fluxo de reprocessamento idempotente;
- se houver dados suficientes para projeção futura, seguir para `project_future_installments`; caso contrário, registrar limitação explicitamente.

## Onde o agente realmente ajuda

O componente “agente” ajuda em casos restritos:

- interpretar linhas ambíguas;
- normalizar descrições variantes do mesmo lojista;
- ajudar no matching histórico de parcelamentos quando a heurística falhar.

Fora disso, agente livre tende a piorar:

- auditabilidade;
- previsibilidade;
- custo;
- reprodutibilidade.

## Contratos Pydantic recomendados

Modelos centrais sugeridos para a v1:

- `InvoiceInput`
- `RawInvoiceDocument`
- `InvoiceHeader`
- `TransactionCandidate`
- `TransactionLine`
- `InstallmentCandidate`
- `InstallmentPlan`
- `FutureInstallmentProjection`
- `MonthlyCardSummary`
- `ReviewItem`
- `ProcessingReport`

## Provenance e auditabilidade

Cada entidade persistida deve carregar evidência de origem. Campos recomendados:

- `source_file`
- `page_number`
- `raw_text`
- `bbox | None`
- `extraction_method`
- `confidence`

Sem isso, qualquer correção posterior vira adivinhação.

## Estratégia técnica recomendada

A ordem de prioridade recomendada para o pipeline é:

1. `OpenDataLoader JSON` como fonte primária;
2. `markdown` como apoio contextual;
3. parser por regras por emissor ou layout;
4. fallback LLM com saída Pydantic;
5. revisão humana para baixa confiança.

Essa ordem reduz custo, aumenta previsibilidade e mantém o sistema explicável.

## Consultas que a estrutura final deve suportar

O desenho acima deve permitir consultas como:

- quais parcelas eu tenho neste mês;
- quais parcelas eu tenho no próximo mês;
- quais compras novas fiz neste mês;
- qual o gasto total do mês por cartão;
- quanto de compras parceladas ainda resta por cartão;
- quanto da próxima fatura já está comprometido por parcelas conhecidas;
- qual a diferença entre compra parcelada e parcelamento da própria fatura.

## Próximo refinamento recomendado

Sem implementar nada ainda, o próximo passo mais útil é definir os modelos Pydantic da v1, campo por campo, e depois o modelo canônico de persistência.

Esse é o passo que realmente fecha a arquitetura, porque obriga a decidir:

- o que é uma transação;
- o que é um plano parcelado;
- o que é uma projeção futura;
- o que é evidência suficiente para auditoria e correção.
