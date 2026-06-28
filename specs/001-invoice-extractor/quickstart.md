# Quickstart: Extrator de Faturas Estruturadas

## Objective

Validar a v1 do pipeline ponta a ponta usando PDFs de exemplo, persistência local e consultas por CLI.

## Prerequisites

- Python 3.14 disponível no ambiente do repositório
- Dependências instaladas conforme `pyproject.toml`
- PDFs de exemplo disponíveis em um diretório local
- Permissão de escrita para o banco SQLite e artefatos intermediários

## Suggested Project Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Validation Scenario 1: Processar uma fatura suportada

```bash
python -m faturama.cli process-invoice \
  --pdf-path "samples/invoice-2026-04.pdf" \
  --user-id demo-user \
  --timezone America/Sao_Paulo
```

**Expected outcome**:

- um documento canônico é criado ou reaproveitado por hash;
- a fatura recebe competência, cartão e totais principais;
- transações relevantes são persistidas com evidência de origem;
- o resumo final informa quantidade de transações, planos parcelados, projeções e itens de revisão;
- todo item abaixo do limiar configurado aparece na fila de revisão, sem bloquear a persistência segura do restante da fatura.

## Validation Scenario 2: Reprocessar o mesmo arquivo

```bash
python -m faturama.cli process-invoice \
  --pdf-path "samples/invoice-2026-04.pdf" \
  --user-id demo-user \
  --timezone America/Sao_Paulo
```

**Expected outcome**:

- nenhum documento, transação ou projeção duplicada é criada;
- o relatório indica reprocessamento idempotente.

## Validation Scenario 3: Consultar gasto mensal por cartão

```bash
python -m faturama.cli monthly-spend \
  --user-id demo-user \
  --month 2026-04 \
  --format json
```

**Expected outcome**:

- retorno com totais por cartão;
- compras novas, parcelas cobradas e encargos separados;
- sem mistura entre observado e projetado.

Consulte os campos esperados em [contracts/read-model.md](./contracts/read-model.md).

## Validation Scenario 4: Consultar parcelas do próximo mês

```bash
python -m faturama.cli future-installments \
  --user-id demo-user \
  --month 2026-05 \
  --format json
```

**Expected outcome**:

- lista de projeções futuras por plano parcelado;
- número da parcela projetada, total de parcelas e valor previsto;
- confiança e status da projeção disponíveis para auditoria;
- cada plano projetado pode ser rastreado até uma chave canônica inicial baseada em descrição normalizada, valor da parcela, cartão e data aproximada.

## Validation Scenario 5: Revisar um item ambíguo

```bash
python -m faturama.cli review-queue \
  --user-id demo-user \
  --format table
```

Depois de escolher um item:

```bash
python -m faturama.cli resolve-review \
  --review-item-id <review_id> \
  --resolution accepted \
  --note "Confirmado manualmente"
```

**Expected outcome**:

- o item de revisão muda de estado;
- o sistema registra a decisão;
- entidades dependentes podem ser reavaliadas incrementalmente.

## Validation Status

Os cenários centrais desta v1 foram automatizados na suíte do repositório:

- `tests/contract/`
- `tests/integration/`
- `tests/e2e/test_invoice_pipeline_e2e.py`

Validação local mais recente da implementação: `22 passed`.

## Test Guidance

- Testes unitários devem cobrir parsing monetário, parsing de data, classificação de tipo de transação e regras de matching.
- Testes de integração devem cobrir persistência SQLite, idempotência, snapshots mensais e fila de revisão.
- Testes de contrato devem validar a superfície da CLI e os formatos de saída documentados em [contracts/cli.md](./contracts/cli.md).
- Testes e2e devem usar ao menos duas faturas consecutivas com parcelamento explícito para validar projeções e saldo restante.
