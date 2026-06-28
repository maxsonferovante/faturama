# Contratos de Consulta da v1

## Objetivo

Este documento define os contratos de consulta da v1 do sistema de extração e estruturação de faturas.

O objetivo é deixar explícito:

- quais perguntas o sistema precisa responder;
- quais entidades canônicas sustentam essas respostas;
- quais filtros, agrupamentos e ordenações cada consulta exige;
- quais campos precisam estar persistidos;
- quais materializações valem a pena manter para desempenho e simplicidade.

Sem esse fechamento, o pipeline pode até estruturar bem os dados, mas ainda assim deixar lacunas para o produto final responder as consultas que motivaram o projeto.

## Escopo

Este documento cobre:

- consultas operacionais e analíticas da v1;
- contratos lógicos de entrada e saída das consultas;
- requisitos mínimos de persistência para suportar essas respostas;
- sugestões de views ou tabelas derivadas.

Não cobre:

- design de API HTTP;
- interface de usuário;
- autenticação;
- paginação detalhada de front-end;
- otimização física específica de banco.

## Princípios

### 1. As consultas devem nascer do caso de uso real

O projeto existe para responder perguntas financeiras práticas, não para apenas armazenar documentos parseados.

### 2. Consulta precisa de contrato estável

Cada pergunta importante deve ter:

- entrada clara;
- saída clara;
- semântica estável;
- origem consistente no modelo canônico.

### 3. Nem toda resposta deve ser montada on the fly

Algumas respostas podem vir diretamente de tabelas base.
Outras justificam materialização por serem recorrentes, agregadas ou compostas.

### 4. Projeção e observação devem continuar separadas

Consultas sobre passado e presente usam transações observadas.
Consultas sobre futuro usam projeções derivadas.
Misturar isso sem deixar explícito gera respostas enganosas.

## Categorias de consulta

As consultas da v1 se organizam em 5 grupos:

1. faturas e metadados;
2. transações do mês;
3. parcelamentos e saldo futuro;
4. agregados mensais por cartão;
5. auditoria e revisão.

## 1. Consultas de faturas e metadados

## Q1. Listar faturas disponíveis

### Pergunta de negócio

Quais faturas já foram processadas para um usuário, por cartão e competência?

### Entrada lógica

- `user_id`
- filtro opcional por `card_fingerprint`
- filtro opcional por intervalo de competência

### Saída esperada

Lista de faturas com:

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

### Fonte principal

- tabela `statements`

### Ordenação sugerida

- competência descendente;
- depois vencimento descendente.

### Materialização

- não obrigatória;
- `statements` já atende bem.

## Q2. Obter detalhes de uma fatura

### Pergunta de negócio

Quais são os metadados principais de uma fatura específica?

### Entrada lógica

- `statement_id`

### Saída esperada

- metadados da fatura;
- totais principais;
- confiança;
- indicadores de revisão pendente;
- vínculo com documento de origem.

### Fonte principal

- `statements`
- `documents`
- `review_items`

### Materialização

- não necessária na v1.

## 2. Consultas de transações do mês

## Q3. Listar transações de uma fatura

### Pergunta de negócio

Quais lançamentos compõem esta fatura?

### Entrada lógica

- `statement_id`
- filtros opcionais por:
- `transaction_kind`
- `is_installment`
- `review_status`

### Saída esperada

Lista de transações com:

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

### Fonte principal

- `transactions`

### Ordenação sugerida

- data ascendente ou descendente;
- com fallback em ordem de criação.

### Materialização

- não necessária.

## Q4. Quais compras novas eu fiz neste mês?

### Pergunta de negócio

Quais compras novas foram feitas na competência selecionada?

### Entrada lógica

- `user_id`
- `billing_year`
- `billing_month`
- filtro opcional por cartão

### Saída esperada

Lista de transações filtradas em:

- `transaction_kind = new_purchase`

Com campos:

- cartão;
- data;
- descrição;
- valor;
- confiança;
- eventual categoria auxiliar.

### Fonte principal

- `transactions`
- `statements`

### Materialização

- opcional;
- a consulta direta é suficiente na v1.

## Q5. Quais parcelas estão cobradas neste mês?

### Pergunta de negócio

Quais parcelas efetivamente entraram nesta competência?

### Entrada lógica

- `user_id`
- `billing_year`
- `billing_month`
- filtro opcional por cartão

### Saída esperada

Lista de transações com:

- `transaction_kind = installment_charge`

Campos recomendados:

- `transaction_id`
- `card_fingerprint`
- `description_anchor` ou descrição normalizada;
- `installment_current`
- `installment_total`
- `amount`
- `installment_plan_id`
- `plan_status`

### Fonte principal

- `transactions`
- `installment_plans`

### Materialização

- não obrigatória;
- mas uma view pode ajudar na clareza.

## Q6. Quanto eu gastei no mês por cartão?

### Pergunta de negócio

Qual foi o total gasto por cartão na competência selecionada?

### Entrada lógica

- `user_id`
- `billing_year`
- `billing_month`

### Saída esperada

Por cartão:

- `card_fingerprint`
- `issuer_name`
- `card_label`
- `statement_total_amount`
- `new_purchase_total`
- `installment_charge_total`
- `invoice_financing_total`
- `interest_and_fees_total`

### Fonte principal

- `monthly_card_summaries`

### Materialização

- recomendada.

Motivo:

- é consulta recorrente;
- é agregada;
- é uma das principais do produto.

## 3. Consultas de parcelamentos e saldo futuro

## Q7. Quais parcelas eu tenho no próximo mês?

### Pergunta de negócio

Quais parcelas já conhecidas devem compor a próxima competência?

### Entrada lógica

- `user_id`
- `projected_billing_year`
- `projected_billing_month`
- filtro opcional por cartão

### Saída esperada

Lista de projeções com:

- `projection_id`
- `card_fingerprint`
- `installment_plan_id`
- `description_anchor`
- `projected_installment_number`
- `installment_total`
- `projected_amount`
- `projection_confidence`
- `projection_status`

### Fonte principal

- `future_installment_projections`
- `installment_plans`

### Materialização

- não obrigatória;
- a própria tabela de projeção já é uma materialização útil.

## Q8. Quanto eu ainda tenho de compras parceladas por cartão?

### Pergunta de negócio

Qual é o saldo restante de compras parceladas ainda não quitadas, por cartão?

### Entrada lógica

- `user_id`
- filtro opcional por cartão

### Saída esperada

Por cartão:

- total futuro projetado;
- quantidade de planos ativos;
- próxima parcela total prevista;
- saldo remanescente agregado.

### Fonte principal

- `future_installment_projections`
- `installment_plans`

### Materialização

- recomendada via agregação ou snapshot.

Motivo:

- consulta central;
- depende de soma futura;
- pode ser pedida com frequência.

## Q9. Detalhar um plano parcelado

### Pergunta de negócio

Qual é o histórico e o saldo de uma compra parcelada específica?

### Entrada lógica

- `installment_plan_id`

### Saída esperada

- dados do plano;
- ocorrências já cobradas;
- projeções futuras;
- saldo restante;
- última parcela observada;
- próxima parcela projetada;
- confiança do plano.

### Fonte principal

- `installment_plans`
- `installment_occurrences`
- `future_installment_projections`

### Materialização

- útil manter `InstallmentPlanSnapshot`.

## Q10. Quanto da próxima fatura já está comprometido?

### Pergunta de negócio

Quanto da próxima competência já está comprometido por parcelas conhecidas?

### Entrada lógica

- `user_id`
- `card_fingerprint`
- próxima competência alvo

### Saída esperada

- total projetado de parcelas;
- lista de planos que compõem esse valor;
- confiança agregada da projeção.

### Fonte principal

- `future_installment_projections`

### Materialização

- opcional;
- agregação simples costuma bastar.

## Q11. Qual o saldo restante de cada compra parcelada?

### Pergunta de negócio

Quanto falta pagar em cada plano parcelado ativo?

### Entrada lógica

- `user_id`
- filtro opcional por cartão
- filtro opcional por status do plano

### Saída esperada

Por plano:

- descrição âncora;
- cartão;
- total de parcelas;
- última parcela cobrada;
- parcelas restantes;
- saldo restante;
- próxima parcela prevista.

### Fonte principal

- `installment_plans`
- `installment_occurrences`
- `future_installment_projections`

### Materialização

- recomendada via `InstallmentPlanSnapshot`.

## 4. Consultas de agregados mensais e séries históricas

## Q12. Evolução mensal de gastos por cartão

### Pergunta de negócio

Como os gastos evoluíram ao longo dos meses por cartão?

### Entrada lógica

- `user_id`
- intervalo de competências
- filtro opcional por cartão

### Saída esperada

Série temporal com:

- competência;
- cartão;
- total da fatura;
- compras novas;
- parcelas;
- juros e encargos;
- parcelamento de fatura.

### Fonte principal

- `monthly_card_summaries`

### Materialização

- recomendada.

## Q13. Evolução mensal do saldo parcelado futuro

### Pergunta de negócio

O saldo parcelado futuro está aumentando ou diminuindo ao longo do tempo?

### Entrada lógica

- `user_id`
- intervalo de competências
- filtro opcional por cartão

### Saída esperada

Série temporal com:

- competência de referência;
- saldo futuro total;
- total projetado do próximo mês;
- quantidade de planos ativos.

### Fonte principal

- `monthly_card_summaries`
- ou snapshot derivado dos planos.

### Materialização

- recomendada.

## 5. Consultas de auditoria e revisão

## Q14. Quais itens estão pendentes de revisão?

### Pergunta de negócio

Quais entidades ainda exigem revisão manual?

### Entrada lógica

- `user_id`
- filtros opcionais por:
- `entity_type`
- `severity`
- `status`

### Saída esperada

Lista de itens com:

- `review_item_id`
- `entity_type`
- `entity_id`
- `reason_code`
- `reason_detail`
- `severity`
- `status`
- `created_at`

### Fonte principal

- `review_items`

### Materialização

- não necessária.

## Q15. Por que essa transação ou plano foi classificado assim?

### Pergunta de negócio

Qual foi a evidência e a decisão de confiança por trás de uma entidade?

### Entrada lógica

- `entity_type`
- `entity_id`

### Saída esperada

- metadados da entidade;
- evidências associadas;
- decisão de confiança;
- origem principal;
- se houve conflito entre fontes.

### Fonte principal

- entidade base;
- `source_evidences`;
- eventual tabela de registro de decisão.

### Materialização

- não obrigatória, mas o registro de decisão precisa existir.

## Campos mínimos que precisam estar persistidos

Para que esses contratos funcionem bem, alguns campos não podem faltar.

## Campos mínimos em `statements`

- `statement_id`
- `user_id`
- `card_fingerprint`
- `issuer_name`
- `card_label`
- `card_last4`
- `billing_year`
- `billing_month`
- `statement_due_date`
- `statement_total_amount`
- `statement_status`
- `parse_confidence`

## Campos mínimos em `transactions`

- `transaction_id`
- `statement_id`
- `card_fingerprint`
- `transaction_kind`
- `posted_date`
- `purchase_date`
- `description_raw`
- `description_normalized`
- `merchant_normalized`
- `amount`
- `is_installment`
- `installment_current`
- `installment_total`
- `installment_plan_id`
- `parse_confidence`
- `review_status`

## Campos mínimos em `installment_plans`

- `installment_plan_id`
- `card_fingerprint`
- `description_anchor`
- `installment_total`
- `installment_amount`
- `installment_type`
- `plan_status`
- `plan_confidence`

## Campos mínimos em `future_installment_projections`

- `projection_id`
- `installment_plan_id`
- `card_fingerprint`
- `projected_billing_year`
- `projected_billing_month`
- `projected_installment_number`
- `projected_amount`
- `projection_status`
- `projection_confidence`

## Campos mínimos em `review_items`

- `review_item_id`
- `entity_type`
- `entity_id`
- `reason_code`
- `reason_detail`
- `severity`
- `status`

## Materializações recomendadas para a v1

Nem tudo precisa ser materializado. Para a v1, as materializações mais úteis são estas:

## 1. `monthly_card_summaries`

### Papel

Responder rapidamente:

- total do mês por cartão;
- composição do gasto;
- evolução mensal;
- saldo futuro agregado por competência.

### Justificativa

- consulta recorrente;
- alta legibilidade;
- simplifica consumo.

## 2. `InstallmentPlanSnapshot`

### Papel

Responder rapidamente:

- estado atual de cada compra parcelada;
- saldo restante;
- parcelas restantes;
- próxima projeção.

### Justificativa

- evita recomputar tudo a cada consulta;
- simplifica produto e auditoria.

## 3. tabela de projeções futuras

### Papel

Responder diretamente:

- parcelas do próximo mês;
- saldo projetado por período;
- comprometimento futuro.

### Justificativa

- a própria projeção já é um artefato derivado importante;
- vale persistir como entidade de primeira classe.

## Contratos lógicos de saída

Mesmo sem definir API ainda, a semântica das saídas deve seguir algumas regras:

### 1. Respostas sobre passado e presente

Devem usar:

- transações observadas;
- ocorrências reais;
- faturas já processadas.

### 2. Respostas sobre futuro

Devem usar:

- projeções;
- snapshots de planos parcelados;
- confiança explícita.

### 3. Respostas agregadas

Devem deixar claro:

- competência de referência;
- escopo por cartão ou global;
- se o valor inclui apenas observado ou observado + projetado.

## Regras de semântica importantes

### 1. “Gasto do mês” precisa ser definido com clareza

Na v1, a recomendação é expor separadamente:

- compras novas do mês;
- parcelas cobradas no mês;
- total da fatura;
- encargos e ajustes.

Motivo:

- “gasto do mês” sozinho pode ser ambíguo.

### 2. “Próxima fatura” não é sinônimo de projeção total futura

É preciso separar:

- próxima competência;
- demais competências futuras.

### 3. Saldo parcelado futuro não inclui parcelamento de fatura por padrão

A recomendação é separar:

- compras parceladas no lojista;
- parcelamento da própria fatura.

Se o produto quiser um consolidado total no futuro, isso deve ser uma visão derivada explícita.

## Prioridade de entrega das consultas na v1

Se for necessário priorizar, a ordem mais útil é:

1. listar faturas;
2. listar transações de uma fatura;
3. compras novas do mês;
4. parcelas cobradas no mês;
5. parcelas do próximo mês;
6. total do mês por cartão;
7. saldo restante por compra parcelada;
8. itens pendentes de revisão.

## Decisões fechadas por este documento

Este documento fecha as seguintes decisões:

1. O sistema precisa expor consultas tanto observadas quanto projetadas.
2. `monthly_card_summaries` é materialização recomendada da v1.
3. `InstallmentPlanSnapshot` é materialização recomendada da v1.
4. A tabela de projeções futuras é uma entidade de consulta de primeira classe.
5. Consultas de gasto devem separar compras novas, parcelas e encargos.
6. Consultas futuras devem deixar explícito que são projeções.

## Próximo passo lógico

O próximo refinamento útil, ainda sem implementação, é escrever um `roadmap_v1.md` que organize tudo o que já foi definido em:

- escopo fechado da v1;
- ordem de implementação;
- entregas incrementais;
- riscos técnicos;
- critérios objetivos de pronto.
