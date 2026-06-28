# CLI Contract: Alinhamento de Runtime da Arquitetura

## Purpose

Definir a superfície operacional que deve permanecer estável enquanto o runtime interno passa a usar `OpenDataLoader` e `LangGraph` de forma real.

## Base Command

```bash
python3 -m faturama.cli <command> [options]
```

## Commands

### `process-invoice`

Processa um PDF individual pelo workflow oficial.

**Input**:

```text
process-invoice --pdf-path <path> --user-id <id> [--issuer-hint <issuer>] [--currency BRL] [--timezone America/Sao_Paulo]
```

**Behavior**:

- inicia uma execução oficial do workflow;
- gera ou reaproveita artefatos primários do PDF dentro do runtime;
- coordena parsing, ambiguidades, persistência e resumo sob o mesmo fluxo;
- abre revisão quando necessário sem abandonar o workflow oficial;
- retorna um resumo observável do job.

**Output shape**:

```json
{
  "job_id": "string",
  "document_id": "string",
  "statement_ids": ["string"],
  "status": "parsed|partial|review_required",
  "transactions_persisted": 0,
  "installment_plans_updated": 0,
  "projections_updated": 0,
  "review_items_opened": 0,
  "source_pdf_path": "string"
}
```

### `process-batch`

Processa todos os PDFs de um diretório usando o mesmo workflow oficial por arquivo.

**Input**:

```text
process-batch --input-dir <path> --user-id <id> [--issuer-hint <issuer>] [--fail-fast]
```

**Output shape**:

```json
{
  "batch_id": "string",
  "processed": 0,
  "succeeded": 0,
  "partial": 0,
  "review_required": 0,
  "failed": 0
}
```

### `review-queue`

Lista pendências abertas pelo ramo de revisão do workflow.

**Input**:

```text
review-queue --user-id <id> [--entity-type <type>] [--status <status>] [--severity <level>] [--format json]
```

### `resolve-review`

Registra a resolução de um item pendente e habilita retomada segura do fluxo.

**Input**:

```text
resolve-review --review-item-id <id> --resolution <accepted|rejected|edited> [--note <text>] [--payload-file <path>]
```

**Behavior**:

- vincula a decisão ao item revisado;
- mantém rastreabilidade da origem da decisão;
- permite que a execução seja retomada sem duplicar efeitos anteriores.

### Query Commands Preserved

Os comandos abaixo permanecem estáveis como contrato externo e não devem regredir por causa da troca do runtime interno:

- `list-statements`
- `show-statement`
- `list-transactions`
- `monthly-spend`
- `current-installments`
- `future-installments`
- `remaining-balance`

## Operational Guarantees

- O usuário não precisa conhecer o caminho interno de execução para usar o CLI.
- `process-invoice` e `process-batch` devem continuar idempotentes para o mesmo documento.
- Revisão e retomada não podem exigir regeneração manual de sidecars externos ao runtime.
- O status retornado pelo CLI deve refletir o estado final observável da execução oficial.

## Error Contract

- código de saída `0` em sucesso operacional;
- código diferente de `0` em erro estrutural ou validação;
- quando aplicável, a saída JSON deve incluir `error_code`, `message` e `details`;
- falha de revisão ou pausa deliberada não equivalem, por si só, a erro estrutural do comando.
