# CLI Contract: Extrator de Faturas Estruturadas

## Purpose

Definir a superfície inicial de uso do sistema na v1 para processamento, consulta e revisão operacional.

## Command Group

Base command:

```bash
python -m faturama.cli <command> [options]
```

## Commands

### `process-invoice`

Processa um PDF individual e atualiza a base canônica.

**Input**:

```text
process-invoice --pdf-path <path> --user-id <id> [--issuer-hint <issuer>] [--currency BRL] [--timezone America/Sao_Paulo]
```

**Behavior**:

- registra o documento por hash;
- extrai artefatos brutos;
- estrutura cabeçalho e transações;
- reconcilia parcelamentos e projeções;
- persiste resultados e pendências;
- abre fila de revisão para todo item abaixo do limiar configurado;
- responde com resumo do job.

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
  "review_items_opened": 0
}
```

### `process-batch`

Processa um diretório ou lista de PDFs.

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

### `list-statements`

Lista faturas processadas por usuário.

**Input**:

```text
list-statements --user-id <id> [--card <fingerprint>] [--from YYYY-MM] [--to YYYY-MM]
```

**Output shape**:

- tabela humana por padrão;
- `--format json` retorna uma lista de objetos com os campos do contrato Q1.

### `show-statement`

Exibe detalhes de uma fatura e seus totais principais.

**Input**:

```text
show-statement --statement-id <id> [--format table|json]
```

### `list-transactions`

Lista transações de uma fatura.

**Input**:

```text
list-transactions --statement-id <id> [--kind <transaction_kind>] [--installments-only] [--review-status <status>] [--format table|json]
```

### `monthly-spend`

Retorna agregados mensais por cartão.

**Input**:

```text
monthly-spend --user-id <id> --month YYYY-MM [--card <fingerprint>] [--format table|json]
```

**Output fields**:

- `card_fingerprint`
- `issuer_name`
- `card_label`
- `statement_total_amount`
- `new_purchase_total`
- `installment_charge_total`
- `invoice_financing_total`
- `interest_and_fees_total`

### `current-installments`

Lista parcelas observadas na competência escolhida.

**Input**:

```text
current-installments --user-id <id> --month YYYY-MM [--card <fingerprint>] [--format table|json]
```

### `future-installments`

Lista parcelas previstas para uma competência futura.

**Input**:

```text
future-installments --user-id <id> --month YYYY-MM [--card <fingerprint>] [--format table|json]
```

### `remaining-balance`

Mostra saldo restante por compra parcelada ou consolidado por cartão.

**Input**:

```text
remaining-balance --user-id <id> [--card <fingerprint>] [--plan-id <installment_plan_id>] [--format table|json]
```

### `review-queue`

Lista itens pendentes de revisão.

**Input**:

```text
review-queue --user-id <id> [--entity-type <type>] [--status <status>] [--severity <level>] [--format table|json]
```

### `resolve-review`

Aplica uma decisão manual a um item de revisão e habilita retomada do fluxo.

**Input**:

```text
resolve-review --review-item-id <id> --resolution <accepted|rejected|edited> [--note <text>] [--payload-file <path>]
```

**Behavior**:

- atualiza a entidade alvo;
- registra a resolução;
- permite reavaliação incremental de projeções e resumos impactados.
- fecha explicitamente a pendência criada por confiança abaixo do limiar ou conflito material.

## Error Contract

Todos os comandos devem retornar:

- código de saída `0` em sucesso;
- código diferente de `0` em erro operacional ou validação;
- mensagem amigável em stderr;
- `--format json` inclui `error_code`, `message` e `details` quando aplicável.

## Idempotency Expectations

- `process-invoice` pode ser executado repetidamente para o mesmo arquivo sem duplicar entidades canônicas.
- `resolve-review` deve ser seguro contra reaplicação idêntica e registrar conflito quando uma revisão já estiver resolvida.
