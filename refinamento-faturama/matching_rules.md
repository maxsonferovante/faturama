# Regras de Matching para Agrupamento de Parcelas e Deduplicação de Transações

## Objetivo

Este documento define as regras funcionais e técnicas da v1 para:

- deduplicar transações extraídas de uma mesma fatura;
- agrupar parcelas mensais em um mesmo `InstallmentPlan`;
- decidir quando um vínculo é confiável, ambíguo ou deve ir para revisão.

O foco não é implementar heurísticas ainda, mas fechar a lógica de decisão do pipeline.

## Escopo

Este refinamento cobre:

- matching dentro da mesma fatura;
- matching entre faturas diferentes do mesmo cartão;
- agrupamento de compras parceladas;
- distinção entre compra parcelada e parcelamento de fatura;
- critérios de confiança;
- critérios de revisão manual.

Não cobre:

- categorização financeira por tipo de estabelecimento;
- enriquecimento externo de lojistas;
- reconciliação com extrato bancário ou Open Finance;
- matching entre cartões diferentes.

## Princípios

### 1. Melhor não agrupar do que agrupar errado

Um falso positivo no agrupamento de parcelas é pior do que deixar duas séries separadas temporariamente.

### 2. Matching deve ser explicável

Toda decisão de matching precisa ser justificável por sinais observáveis:

- descrição;
- valor;
- número da parcela;
- total de parcelas;
- competência;
- cartão;
- datas;
- evidência de origem.

### 3. Regras primeiro, inferência depois

O matching deve seguir esta ordem:

1. regra exata;
2. heurística forte;
3. heurística fraca;
4. auxílio de LLM;
5. revisão manual.

### 4. Cartão é fronteira primária

Por padrão, não se deve agrupar transações de cartões diferentes no mesmo `InstallmentPlan`, mesmo quando a descrição parecer igual.

## Parte 1: Deduplicação de transações

## Objetivo da deduplicação

Evitar que a mesma linha financeira vire duas ou mais `TransactionLine` canônicas por causa de:

- repetição no `markdown` e no `json`;
- linha quebrada em múltiplos blocos;
- múltiplas passagens de parsing;
- reprocessamento do mesmo PDF;
- sobreposição entre parser por regra e fallback LLM.

## Níveis de deduplicação

### Nível A: deduplicação documental

Antes de qualquer parsing detalhado, o documento deve ser tratado como reprocessamento do mesmo artefato se:

- `file_hash` for igual a um documento já persistido.

Resultado esperado:

- não recriar `documents`;
- não recriar `statements`;
- não recriar `transactions` sem necessidade;
- permitir reprocessamento versionado se explicitamente desejado.

### Nível B: deduplicação intra-fatura

Dentro da mesma fatura, duas transações candidatas devem ser consideradas duplicadas quando representam a mesma linha financeira observada no documento.

### Nível C: deduplicação interprocessamento

No reprocessamento da mesma fatura com regras melhores, a deduplicação deve impedir regravação duplicada da mesma transação lógica.

## Chave lógica sugerida para deduplicação intra-fatura

A comparação deve considerar, nesta ordem:

1. `statement_id`
2. `card_fingerprint`
3. `amount`
4. `posted_date` ou `purchase_date`
5. `description_raw` normalizada
6. `installment_current`
7. `installment_total`
8. `page_number`
9. `line_hash`

## Normalização mínima para comparação de descrições

Antes do matching textual, a descrição usada para deduplicação deve:

- converter para caixa única;
- remover espaços duplicados;
- remover pontuação irrelevante;
- normalizar acentos quando útil;
- padronizar abreviações simples se forem recorrentes;
- remover variações cosméticas que não mudem o lojista.

Exemplos:

- `MERCADOLIVRE*MERCADOL`
- `MERCADO*MERCADOLIVRE`

Essas descrições podem convergir para uma chave textual comparável, mas a normalização não deve apagar informação de parcela.

## Regras de deduplicação intra-fatura

### Regra D1: duplicata exata

Considerar duplicata quando houver igualdade em:

- `statement_id`
- `amount`
- data principal
- descrição normalizada
- `installment_current`
- `installment_total`

Decisão:

- manter só uma transação canônica;
- unir evidências das duas origens.

### Regra D2: duplicata por origem fragmentada

Considerar duplicata quando:

- os valores são iguais;
- a data é igual;
- uma descrição é subconjunto claro da outra;
- as evidências vêm da mesma página e região próxima;
- uma origem veio de bloco quebrado e a outra de bloco consolidado.

Decisão:

- manter a transação com descrição mais completa;
- anexar as demais como evidência complementar.

### Regra D3: parser por regra vs fallback LLM

Quando uma linha foi resolvida tanto por regra quanto por LLM, considerar a mesma transação se:

- compartilham a mesma evidência principal;
- possuem valor idêntico;
- possuem mesma data ou data compatível;
- a descrição for semanticamente equivalente.

Decisão:

- manter um único registro;
- priorizar os campos da regra quando a confiança estrutural for maior;
- usar o output da LLM apenas para completar campos faltantes ou normalização.

### Regra D4: mesma descrição e mesmo valor, mas datas diferentes

Não deduplicar automaticamente quando:

- a descrição parece igual;
- o valor parece igual;
- mas a data difere de forma material.

Motivo:

- pode ser recorrência real;
- pode ser compra repetida;
- pode ser outra parcela sem identificação explícita.

Decisão:

- manter separado;
- só agrupar se houver outros sinais fortes.

### Regra D5: múltiplas linhas idênticas no mesmo dia

Não deduplicar apenas por semelhança textual quando:

- mesmo lojista;
- mesma data;
- mesmo valor;
- múltiplas ocorrências reais são plausíveis.

Exemplo:

- duas compras iguais no mesmo marketplace.

Decisão:

- manter ambas se vierem de evidências distintas;
- só deduplicar se a evidência apontar que é a mesma linha repetida no parsing.

## Sinais de confiança para deduplicação

### Alta confiança

- mesma evidência principal;
- mesmo valor;
- mesma data;
- mesma descrição normalizada;
- mesmo número e total de parcela, quando houver.

### Média confiança

- mesmo valor;
- mesma data;
- descrição semanticamente muito próxima;
- mesma página;
- regiões próximas.

### Baixa confiança

- só descrição parecida;
- só mesmo valor;
- datas divergentes;
- sem evidência estrutural comum.

## Parte 2: Agrupamento de parcelas em `InstallmentPlan`

## Objetivo do agrupamento

Identificar que parcelas cobradas em meses diferentes pertencem à mesma compra parcelada.

Esse agrupamento é o que permite:

- calcular saldo restante;
- projetar meses futuros;
- saber a origem histórica da dívida parcelada.

## Pré-condições para considerar uma transação como candidata

Uma `TransactionLine` entra na fila de matching de parcelas quando ao menos uma destas condições ocorrer:

- contém padrão explícito `Parcela X de Y`;
- foi classificada como `installment_charge`;
- foi extraída de seção de compras parceladas;
- foi ligada a bloco de “próximas faturas”;
- tem forte sinal textual de parcelamento.

## Sinais principais de agrupamento

Os sinais usados para montar um `InstallmentPlan` devem ser:

1. `card_fingerprint`
2. tipo do parcelamento
3. descrição normalizada
4. valor da parcela
5. total de parcelas
6. número atual da parcela
7. distância temporal entre competências
8. data âncora da compra, quando disponível

## Regras de matching de parcelas

### Regra P1: match exato por texto explícito

Agrupar no mesmo `InstallmentPlan` quando:

- mesmo cartão;
- mesma descrição normalizada;
- mesmo valor de parcela;
- mesmo total de parcelas;
- sequência coerente de `Parcela X de Y` ao longo de competências sucessivas.

Exemplo:

- `Parcela 02 de 10` em maio;
- `Parcela 03 de 10` em junho.

Decisão:

- criar ou atualizar `InstallmentPlan` com alta confiança.

### Regra P2: match exato sem sequência completa, mas com âncora forte

Agrupar quando:

- mesmo cartão;
- mesma descrição normalizada;
- mesmo valor;
- mesmo total de parcelas;
- número da parcela compatível com a diferença entre competências observadas.

Exemplo:

- aparece `08 de 12` numa fatura;
- depois `09 de 12` na seguinte.

Decisão:

- alta confiança.

### Regra P3: descrição variante com valor e sequência coerentes

Agrupar quando:

- mesmo cartão;
- mesmo valor de parcela;
- mesmo total de parcelas;
- descrição com pequena variação textual;
- progressão coerente do número da parcela.

Exemplo:

- `MERCADOLIVRE*MERCADOL`
- `MERCADO*MERCADOLIVRE`

Decisão:

- confiança média ou alta, dependendo da força da normalização.

### Regra P4: mesmo texto e valor, mas total de parcelas diferente

Não agrupar automaticamente quando:

- descrição parece igual;
- valor parece igual;
- total de parcelas difere.

Motivo:

- pode ser nova compra do mesmo lojista;
- pode ser outro parcelamento iniciado depois.

Decisão:

- criar plano separado;
- ou enviar para revisão se houver sinais conflitantes.

### Regra P5: mesmo texto e total, mas valor diferente

Não agrupar automaticamente quando:

- descrição coincide;
- total de parcelas coincide;
- valor da parcela diverge materialmente.

Motivo:

- pode ser compra distinta;
- pode haver ajuste, IOF ou conversão;
- pode ser erro de parsing.

Decisão:

- manter separado;
- revisão manual se o restante dos sinais apontar para o mesmo plano.

### Regra P6: parcela futura projetada vs parcela observada

Quando uma parcela projetada aparece depois como transação real:

- não criar novo plano;
- vincular a transação ao `InstallmentPlan` já existente;
- marcar a projeção correspondente como `realized` ou `superseded`.

### Regra P7: compra parcelada vs parcelamento de fatura

Nunca agrupar no mesmo `InstallmentPlan` uma transação de:

- `installment_charge`

com uma transação de:

- `invoice_installment`

Mesmo que:

- o valor seja parecido;
- o número de parcelas exista;
- a competência seja próxima.

Esses são objetos financeiros diferentes.

### Regra P8: lacuna de competência

Se um plano aparece em um mês e desaparece no seguinte, não encerrar automaticamente o plano sem evidência adicional.

Possíveis causas:

- fatura ausente no histórico;
- erro de extração;
- parcela antecipada;
- estorno;
- cancelamento.

Decisão:

- manter plano como `active` ou `uncertain`;
- reavaliar quando houver mais histórico.

## Estratégia de criação de `InstallmentPlan`

### Caso 1: primeiro avistamento

Quando uma transação parcelada não encontra plano existente com confiança suficiente:

- criar novo `InstallmentPlan`;
- registrar `first_seen_statement_id`;
- registrar estratégia de matching usada.

### Caso 2: atualização de plano existente

Quando o matching encontra plano compatível:

- atualizar o plano;
- registrar `InstallmentOccurrence`;
- recalcular saldo restante;
- recalcular projeções futuras.

### Caso 3: conflito entre múltiplos planos candidatos

Quando mais de um plano parece possível:

- não vincular automaticamente se a diferença de score for pequena;
- criar `ReviewItem`;
- manter a transação com `installment_plan_id = null` até revisão, se necessário.

## Scoring sugerido para agrupamento

O matching pode usar score composto, mesmo sem fixar pesos exatos agora.

Sinais de score positivo:

- mesmo cartão;
- mesmo tipo de parcelamento;
- mesma descrição normalizada;
- mesmo valor;
- mesmo total de parcelas;
- progressão coerente do número da parcela;
- compatibilidade temporal entre competências.

Sinais de penalização:

- total de parcelas diferente;
- valor muito diferente;
- tipo de parcelamento diferente;
- data âncora incompatível;
- plano já encerrado sem evidência de reabertura.

## Faixas de decisão sugeridas

### `auto_match_high`

Condições:

- sinais fortes convergentes;
- nenhuma contradição material.

Decisão:

- vincular automaticamente.

### `auto_match_medium`

Condições:

- sinais suficientes;
- alguma variação textual pequena;
- progressão coerente da parcela.

Decisão:

- vincular automaticamente;
- marcar confiança intermediária.

### `review_required`

Condições:

- sinais mistos;
- mais de um plano candidato plausível;
- diferença pequena entre candidatos;
- conflito entre valor, texto ou total de parcelas.

Decisão:

- encaminhar para revisão.

### `no_match`

Condições:

- ausência de sinais mínimos;
- contradições materiais.

Decisão:

- não vincular;
- criar novo plano, quando fizer sentido.

## Regras de encerramento de plano

Um `InstallmentPlan` pode ser marcado como `completed` quando:

- a última ocorrência observada corresponde à última parcela esperada;
- ou todas as projeções futuras foram realizadas ou canceladas;
- e não há inconsistência aberta.

Um plano pode ser marcado como `uncertain` quando:

- há lacunas no histórico;
- há conflito entre total de parcelas observado e esperado;
- ou o matching histórico ficou incompleto.

## Situações que devem ir para revisão manual

Encaminhar para revisão quando:

- duas compras distintas parecem o mesmo plano;
- o total de parcelas muda no meio da série;
- o valor da parcela muda de forma não explicada;
- há duas ocorrências candidatas para o mesmo número de parcela;
- a progressão temporal não fecha;
- a descrição mudou demais entre meses;
- há dúvida entre `merchant_purchase` e `invoice_financing`;
- há múltiplos planos plausíveis com scores próximos.

## Evidência que deve ser preservada no matching

Para cada decisão de matching, o sistema deve preservar:

- transação de origem;
- plano candidato;
- regra aplicada;
- sinais usados;
- score final;
- confiança final;
- evidência textual relevante.

Sem isso, o agrupamento histórico fica difícil de depurar.

## Exemplos conceituais

### Exemplo 1: match forte

Maio:

- `MERCADOLIVRE ... (Parcela 02 de 10) - R$ 422,89`

Junho:

- `MERCADO*MERCADOLIVRE (Parcela 03 de 10) - R$ 422,89`

Sinais:

- mesmo cartão;
- valor idêntico;
- total de parcelas idêntico;
- progressão de 2 para 3;
- descrição altamente compatível.

Decisão:

- mesmo `InstallmentPlan`.

### Exemplo 2: não agrupar automaticamente

Maio:

- `LOJA X (Parcela 02 de 10) - R$ 150,00`

Junho:

- `LOJA X (Parcela 01 de 6) - R$ 150,00`

Sinais conflitantes:

- mesmo lojista;
- mesmo valor;
- total de parcelas diferente;
- progressão incompatível.

Decisão:

- planos distintos ou revisão.

### Exemplo 3: possível duplicata, mas não deduplicar

Mesmo mês:

- `UBER *TRIP - R$ 24,90`
- `UBER *TRIP - R$ 24,90`

Se vierem de evidências diferentes e sem sinal de repetição estrutural:

- manter as duas transações.

## Decisões fechadas por este refinamento

Este documento fecha as seguintes decisões:

1. Deduplicação e matching são problemas diferentes e devem ser tratados separadamente.
2. O cartão é fronteira primária de agrupamento.
3. Compra parcelada e parcelamento de fatura nunca compartilham o mesmo plano.
4. Matching forte exige coerência entre texto, valor, total de parcelas e progressão temporal.
5. Em caso de dúvida, priorizar separação ou revisão, não agrupamento agressivo.

## Próximo passo lógico

O próximo refinamento útil, ainda sem implementação, é escrever um `confidence_policy.md` para consolidar:

- faixas de confiança;
- gatilhos de revisão humana;
- política de prioridade entre regra, heurística e LLM;
- critérios de aceitação automática por tipo de entidade.
