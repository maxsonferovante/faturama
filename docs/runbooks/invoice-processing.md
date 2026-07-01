# Runbook: Invoice Processing

## Objetivo

Operar a ingestao de faturas com rastreabilidade, idempotencia e revisao manual controlada.

## Fluxo normal

1. Garanta a conexão válida configurada em `FATURAMA_DB_DSN` e permissões de escrita para `FATURAMA_ARTIFACT_CACHE_DIR`.
2. Execute `python3 -m faturama.cli process-invoice --pdf-path <arquivo.pdf> --user-id <id>`.
3. O runtime oficial usa `OpenDataLoader PDF` para gerar ou reutilizar cache `markdown/json` em `FATURAMA_ARTIFACT_CACHE_DIR`.
4. O workflow `LangGraph` percorre extração, parsing, classificação, resolução e persistência com checkpoints PostgreSQL.
5. Consulte o resultado no JSON de saída.
6. Se `status=review_required`, liste pendências com `review-queue`.

## Evidencia persistida

- documento por hash
- fatura canonica por competencia/cartao
- transacoes com `raw_text`, `page_number`, `source_strategy` e `source_evidence_id`
- planos parcelados e projeções futuras
- registros de decisao e fila de revisao

## Reprocessamento

- o mesmo PDF reutiliza `document_id` e `statement_id` deterministico
- transacoes usam `line_hash` estavel por fatura
- planos parcelados usam chave canonica estavel entre meses
- resolucoes humanas persistidas podem ser reaplicadas no proximo processamento do mesmo documento
- registros legados fora do runtime oficial ficam `invalidated` e nao aparecem nas consultas

## Checkpoints

Checkpoints ficam no PostgreSQL (`FATURAMA_DB_DSN`) e registram:

- `job_id`
- `thread_id`
- `node_name`
- status do workflow
- artefatos carregados
- transacoes e review items produzidos

## Diagnostico rapido

- erro de artefato: confirme que o runtime conseguiu escrever em `FATURAMA_ARTIFACT_CACHE_DIR`
- erro de extração complexa: configure `FATURAMA_OPENDATALOADER_HYBRID_URL` e suba o backend híbrido
- duplicacao inesperada: valide `line_hash` e a chave canonica do parcelamento
- pendencia recorrente apos revisao: verifique se o `review_item` foi resolvido e se a nova execucao usou o mesmo PDF/hash
- consulta vazia: confirme `FATURAMA_DB_DSN` apontando para o banco correto

