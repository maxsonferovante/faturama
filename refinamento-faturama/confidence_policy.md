# Política de Confiança, Aceitação Automática e Revisão Manual

## Objetivo

Este documento define a política de confiança da v1 do pipeline de extração e estruturação de faturas.

O foco é responder, de forma consistente:

- quando um dado pode ser aceito automaticamente;
- quando um dado deve ser encaminhado para revisão manual;
- como priorizar resultados vindos de regra, heurística e LLM;
- como transformar confiança em decisão operacional.

Este documento não define pesos numéricos fixos de scoring, mas define a lógica de decisão que a implementação deverá seguir.

## Problema que esta política resolve

O pipeline terá múltiplas fontes de verdade parcial:

- extração estrutural do `OpenDataLoader`;
- regras determinísticas;
- heurísticas de matching;
- LLM com saída estruturada;
- revisão humana.

Sem uma política explícita, o sistema tende a ficar inconsistente em casos ambíguos:

- ora aceita demais;
- ora revisa demais;
- ora deixa a LLM sobrescrever informação estrutural forte;
- ora prende casos simples numa fila manual desnecessária.

Esta política existe para evitar isso.

## Princípios

### 1. Confiar primeiro no sinal mais verificável

A ordem de preferência deve favorecer o que é mais observável e auditável.

Prioridade de evidência:

1. evidência estrutural explícita do documento;
2. regra determinística baseada nessa evidência;
3. heurística com sinais convergentes;
4. LLM com schema válido;
5. revisão humana como decisão final.

### 2. Aceitação automática exige convergência

O sistema só deve aceitar automaticamente quando houver sinais suficientes e sem contradição material.

### 3. Ambiguidade não deve ser escondida

Quando houver conflito real entre interpretações plausíveis, o sistema deve:

- registrar a ambiguidade;
- reduzir a confiança;
- e, se necessário, enviar para revisão.

### 4. Validação estrutural não é confiança semântica

Uma saída da LLM ou de uma regra pode ser estruturalmente válida no schema Pydantic e ainda assim ser semanticamente duvidosa.

Validação de schema garante forma.
Confiança garante aceitabilidade operacional.

### 5. Revisão manual é parte normal do sistema

A revisão manual não é fallback de erro; ela é um mecanismo deliberado para proteger a base canônica em casos de dúvida relevante.

## Fontes de evidência e sua prioridade

## Nível 1: evidência estrutural explícita

Exemplos:

- campo textual claro como `Parcela 03 de 10`;
- valor monetário explícito;
- data explícita;
- seção identificada como despesas ou compras parceladas;
- bloco do cabeçalho com vencimento, total e limite.

Tratamento:

- é a fonte mais forte do sistema;
- deve prevalecer quando não houver contradição.

## Nível 2: regra determinística

Exemplos:

- regex para `Parcela X de Y`;
- parser monetário;
- parser de data;
- mapeamento de seção para tipo de transação;
- detecção de cabeçalho por posição e conteúdo.

Tratamento:

- alta prioridade quando baseada em evidência estrutural clara;
- pode perder força quando operar sobre texto quebrado, ambíguo ou incompleto.

## Nível 3: heurística

Exemplos:

- matching de descrições parecidas;
- agrupamento de parcelas por valor e progressão temporal;
- inferência de vínculo com plano parcelado mesmo com pequena variação textual.

Tratamento:

- serve para completar ou reconciliar;
- não deve sobrescrever evidência estrutural explícita contraditória;
- pode levar à aceitação automática em casos fortes;
- deve ir para revisão em caso de sinais mistos.

## Nível 4: LLM com saída estruturada

Exemplos:

- classificar linha ambígua;
- extrair campos quando a linha está mal formada;
- sugerir descrição normalizada;
- decidir entre dois tipos de transação parecidos quando a regra falhou.

Tratamento:

- é uma fonte auxiliar de interpretação;
- não deve substituir automaticamente dado estrutural forte;
- pode resolver casos que regras e heurísticas não fecham;
- deve sempre ser validada por schema e política de confiança.

## Nível 5: revisão humana

Exemplos:

- conflito entre dois planos parcelados plausíveis;
- divergência material entre valor, texto e progressão;
- dúvida entre compra parcelada e parcelamento de fatura;
- duplicata possível, mas não comprovada.

Tratamento:

- é a autoridade final em casos ambíguos de alto impacto.

## Tipos de confiança

Para a v1, a confiança deve ser pensada em quatro dimensões lógicas:

### 1. Confiança estrutural

Mede o quão bem o dado foi extraído do documento.

Exemplos:

- valor bem capturado;
- data bem capturada;
- linha íntegra;
- seção bem identificada.

### 2. Confiança semântica

Mede o quão correta parece a interpretação do dado.

Exemplos:

- a linha realmente é compra e não juros;
- a ocorrência realmente é parcela;
- o tipo da transação faz sentido no contexto.

### 3. Confiança relacional

Mede o quão confiável é um vínculo entre entidades.

Exemplos:

- transação ligada ao plano parcelado correto;
- projeção ligada ao plano correto;
- duplicata detectada corretamente.

### 4. Confiança operacional

Mede se o sistema pode aceitar aquilo automaticamente sem revisão.

Ela é derivada das outras três e do impacto do erro.

## Faixas de decisão

As decisões operacionais devem cair em 4 estados:

### `accepted_high`

Significa:

- aceitação automática com alta confiança;
- nenhuma ação manual necessária;
- entidade pode ser persistida como válida.

Usar quando:

- sinais estruturais são fortes;
- interpretação é coerente;
- não há contradição material.

### `accepted_medium`

Significa:

- aceitação automática permitida;
- confiança intermediária;
- a entidade pode ser persistida;
- idealmente com marcação de confiança para auditoria futura.

Usar quando:

- os sinais são bons, mas não perfeitos;
- a chance de erro é baixa;
- o impacto do erro é moderado ou baixo.

### `review_required`

Significa:

- a entidade não deve ser descartada;
- mas também não deve virar verdade canônica sem validação humana.

Usar quando:

- há conflito entre sinais;
- há mais de uma interpretação plausível;
- o impacto do erro é relevante.

### `rejected`

Significa:

- a entidade ou vínculo não deve ser aceito;
- pode ser descartada ou marcada como inválida.

Usar quando:

- a evidência é insuficiente;
- o resultado é inconsistente;
- o schema pode até passar, mas a interpretação é materialmente indefensável.

## Política por tipo de entidade

## 1. Cabeçalho da fatura

### Aceitação automática alta

Quando:

- vencimento, total e emissor aparecem claramente;
- os campos foram extraídos de blocos esperados do cabeçalho;
- não há conflito entre valores duplicados no documento.

### Revisão manual

Quando:

- datas conflitantes aparecem em seções diferentes;
- total da fatura aparece com valores inconsistentes;
- cartão ou competência ficam ambíguos.

### Rejeição

Quando:

- o documento não fornece sinal mínimo para identificar a fatura.

## 2. Transação individual

### Aceitação automática alta

Quando:

- data, valor e descrição são claros;
- seção e contexto são compatíveis;
- tipo da transação é inequívoco.

Exemplo:

- compra com valor explícito em seção de despesas;
- parcela explícita com `Parcela X de Y`.

### Aceitação automática média

Quando:

- a estrutura está boa;
- a semântica foi inferida por regra ou heurística razoável;
- não há concorrência com outra interpretação forte.

### Revisão manual

Quando:

- a linha pode ser tanto compra quanto ajuste;
- a descrição está quebrada;
- a data não fecha;
- o valor parece válido, mas o tipo da transação é incerto;
- regra e LLM divergem materialmente.

### Rejeição

Quando:

- a linha não representa lançamento financeiro;
- ou a extração não fornece base mínima de interpretação.

## 3. Deduplicação de transações

### Aceitação automática alta

Quando:

- duas ocorrências compartilham a mesma evidência principal;
- valor, data, descrição e parcela coincidem;
- a duplicidade decorre claramente do parsing.

### Aceitação automática média

Quando:

- a duplicidade é muito provável;
- há pequena variação textual;
- mas a evidência estrutural ainda converge.

### Revisão manual

Quando:

- duas linhas muito parecidas podem ser compras reais distintas;
- o mesmo valor e o mesmo lojista se repetem no mesmo dia;
- há dúvida entre repetição real e duplicata.

### Rejeição do merge

Quando:

- há divergência material de data;
- há evidência distinta para duas transações plausíveis;
- o merge ficaria especulativo.

## 4. Matching de `InstallmentPlan`

### Aceitação automática alta

Quando:

- mesmo cartão;
- mesma descrição normalizada ou altamente equivalente;
- mesmo valor de parcela;
- mesmo total de parcelas;
- progressão temporal coerente do número da parcela.

### Aceitação automática média

Quando:

- há variação textual pequena;
- os demais sinais convergem fortemente;
- não há outro plano concorrente plausível.

### Revisão manual

Quando:

- existem dois ou mais planos candidatos próximos;
- o total de parcelas ou valor diverge;
- a progressão temporal não fecha bem;
- a descrição mudou demais;
- há risco de vincular a compra errada.

### Rejeição do vínculo

Quando:

- o tipo do parcelamento diverge;
- o cartão diverge;
- o valor ou a estrutura contradizem o plano.

## 5. Projeção futura

### Aceitação automática alta

Quando:

- o `InstallmentPlan` está consistente;
- a parcela atual observada é confiável;
- o total de parcelas e o valor estão claros.

### Aceitação automática média

Quando:

- o plano está razoavelmente estável;
- existe pequena incerteza textual, mas a progressão é coerente.

### Revisão manual

Quando:

- o plano de origem já é incerto;
- há lacunas de competência;
- o valor da parcela variou sem explicação;
- a projeção pode induzir consulta errada de saldo futuro.

### Rejeição

Quando:

- não existe base suficiente para projetar com responsabilidade.

## Priorização entre regra, heurística e LLM

## Regra geral de precedência

A precedência deve ser:

1. evidência estrutural explícita;
2. regra determinística;
3. heurística forte;
4. LLM;
5. revisão humana.

## Casos de precedência

### Caso A: regra forte vs LLM divergente

Se a regra estiver baseada em evidência clara e a LLM divergir:

- manter a regra;
- registrar divergência se necessário;
- usar a LLM no máximo para enriquecimento auxiliar.

### Caso B: regra fraca vs LLM coerente

Se a regra estiver apoiada em texto incompleto e a LLM produzir interpretação coerente com o contexto:

- a LLM pode elevar a confiança;
- mas não deve decidir sozinha quando o impacto do erro for alto.

### Caso C: heurística forte vs LLM divergente

Se a heurística tiver sinais múltiplos convergentes e a LLM sugerir outra leitura:

- manter a heurística;
- reduzir confiança apenas se a divergência revelar contradição real.

### Caso D: regra ausente, heurística fraca e LLM válida

Se não houver base forte por regra e a LLM for a única interpretação útil:

- aceitar apenas se:
- a saída estiver no schema;
- o contexto for coerente;
- o impacto do erro for baixo ou moderado;
- não houver interpretação concorrente plausível.

Caso contrário:

- revisão manual.

## Política de conflito

Quando diferentes fontes produzirem resultados divergentes, a decisão deve seguir:

1. verificar se a divergência é real ou apenas cosmética;
2. medir qual fonte tem melhor evidência observável;
3. medir o impacto do erro;
4. decidir entre:
- aceitar uma versão;
- aceitar com confiança reduzida;
- abrir revisão manual;
- rejeitar ambas.

## Impacto do erro

Nem todo erro tem o mesmo custo. A política deve considerar o impacto do erro na decisão.

### Baixo impacto

Exemplos:

- normalização de nome do lojista;
- categoria auxiliar;
- canal de origem da compra.

Nesses casos, o sistema pode aceitar automaticamente com confiança média.

### Médio impacto

Exemplos:

- classificar compra nova vs ajuste simples;
- deduplicar duas linhas muito parecidas;
- projetar parcela futura de plano razoavelmente estável.

Nesses casos, a aceitação automática exige mais convergência.

### Alto impacto

Exemplos:

- vincular transação ao plano parcelado errado;
- confundir compra parcelada com parcelamento de fatura;
- errar saldo restante relevante;
- errar total do mês por cartão.

Nesses casos, a política deve ser conservadora e tender à revisão.

## Gatilhos de revisão manual

Encaminhar para revisão quando ocorrer pelo menos um destes cenários:

- conflito material entre regra e LLM;
- dois ou mais planos parcelados candidatos com score próximo;
- mudança inesperada de valor da parcela;
- mudança inesperada do total de parcelas;
- dúvida entre `merchant_purchase` e `invoice_financing`;
- cabeçalho inconsistente;
- soma das transações incompatível com o total da fatura em grau relevante;
- data ausente ou conflitante em entidade de alto impacto;
- evidência estrutural insuficiente para aceitação segura.

## Política de persistência em caso de dúvida

Quando houver dúvida parcial, o sistema não precisa necessariamente bloquear tudo.

### Persistir normalmente

Quando:

- a entidade está aceita com alta ou média confiança.

### Persistir com pendência

Quando:

- a entidade base é útil e razoavelmente confiável;
- mas algum vínculo ou classificação secundária precisa de revisão.

Exemplo:

- persistir a transação;
- deixar `installment_plan_id = null`;
- abrir `ReviewItem`.

### Não persistir como canônica

Quando:

- a interpretação principal ainda está indefensável.

## Registro de decisão

Cada decisão relevante de confiança deve registrar:

- `entity_type`
- `entity_id`
- `decision_state`
- `confidence_structural`
- `confidence_semantic`
- `confidence_relational`
- `confidence_operational`
- `primary_evidence_source`
- `decision_reason`
- `conflicting_sources`
- `review_required`

Sem esse registro, a política não será auditável.

## Exemplos conceituais

### Exemplo 1: aceitação automática alta

Linha:

- `14 de abr. 2026 MERCADOLIVRE ... (Parcela 02 de 10) - R$ 422,89`

Sinais:

- valor explícito;
- data explícita;
- parcela explícita;
- tipo da transação inequívoco.

Decisão:

- `accepted_high`.

### Exemplo 2: aceitação automática média

Linha:

- descrição ligeiramente truncada;
- valor e data claros;
- seção de despesas confirmada;
- heurística aponta compra nova.

Decisão:

- `accepted_medium`.

### Exemplo 3: revisão manual

Situação:

- duas séries parecidas de parcelas;
- mesmo lojista;
- valores próximos;
- progressão temporal ambígua.

Decisão:

- `review_required`.

### Exemplo 4: rejeição

Linha:

- texto promocional com valor citado;
- sem natureza transacional;
- sem contexto de despesa real.

Decisão:

- `rejected`.

## Decisões fechadas por esta política

Este documento fecha as seguintes decisões:

1. Evidência estrutural e regra determinística têm precedência sobre LLM.
2. LLM é fonte auxiliar de interpretação, não autoridade primária.
3. Aceitação automática depende de convergência, não apenas de schema válido.
4. Entidades de alto impacto exigem política conservadora.
5. Revisão manual é parte normal e explícita da arquitetura.
6. Dúvida parcial pode gerar persistência com pendência, em vez de bloqueio total.

## Próximo passo lógico

O próximo refinamento útil, ainda sem implementação, é escrever um `query_contracts.md` para definir:

- quais consultas a aplicação final precisa expor;
- quais filtros e agregações cada consulta exige;
- quais campos precisam estar materializados para responder rápido;
- quais views ou tabelas derivadas valem a pena manter na v1.
