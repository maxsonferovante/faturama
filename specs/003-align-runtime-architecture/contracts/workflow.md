# Workflow Contract: Alinhamento de Runtime da Arquitetura

## Purpose

Definir o contrato lógico do workflow oficial para que a implementação use `LangGraph` de forma verificável e para que a revisão assistida por IA permaneça auditável.

## Canonical Flow

O workflow oficial deve possuir, no mínimo, estas fases lógicas:

1. `extract_document`
2. `parse_statement`
3. `classify_transactions`
4. `resolve_ambiguities`
5. `persist_canonical_data`
6. `finalize_job`

## State Expectations

O estado compartilhado do workflow deve conseguir carregar, no mínimo:

- identidade do job;
- referência ao PDF de entrada;
- artefatos de extração primária;
- metadados da fatura;
- candidatos e transações estruturadas;
- casos de revisão abertos;
- contadores de persistência;
- referência ao checkpoint ativo.

## Review Branch Contract

Quando a execução identificar ambiguidade material ou confiança abaixo do limiar:

- o workflow deve encaminhar o caso para `resolve_ambiguities`;
- o ramo assistido por IA pode receber contexto estruturado do documento por página;
- o caso pode ser aceito automaticamente, devolvido para edição humana ou pausado para retomada posterior;
- qualquer pausa deve deixar um checkpoint restaurável.

## Checkpoint and Resume Contract

- cada checkpoint deve estar associado a um `job_id` e a um `node_name`;
- a retomada deve reaproveitar estado persistido e não recriar efeitos já aplicados;
- pontos de pausa devem ocorrer antes de efeitos não idempotentes ou depois de efeitos seguros para repetição;
- payloads usados para pausa e retomada devem ser serializáveis.

## Artifact Contract

- o PDF de entrada é a única entrada documental obrigatória do processamento oficial;
- Markdown e JSON passam a ser artefatos produzidos ou reaproveitados pelo próprio workflow;
- qualquer reutilização de artefato deve permanecer vinculada ao mesmo documento por hash e contexto de origem.

## Completion Contract

Uma execução concluída do workflow deve terminar em uma destas condições:

- `parsed`: persistência completa sem revisão pendente;
- `review_required`: persistência segura do que era possível e pendência aberta para continuação;
- `partial`: alguma parte do fluxo foi concluída, mas com limitação operacional explícita;
- `failed`: o workflow não conseguiu avançar de forma segura.
