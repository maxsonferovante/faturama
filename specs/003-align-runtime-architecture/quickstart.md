# Quickstart: Alinhamento de Runtime da Arquitetura

## Objective

Validar que o pipeline de faturas passou a usar `OpenDataLoader` e `LangGraph` em runtime real, sem perder revisão operacional, persistência canônica e consultas existentes.

## Prerequisites

- Python 3.12+ disponível no ambiente do repositório
- Java 11+ disponível no `PATH`
- dependências instaladas conforme `pyproject.toml`
- PDFs de exemplo acessíveis localmente
- permissão de escrita para banco SQLite, checkpoints e artefatos extraídos

## Suggested Project Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Se o cenário incluir PDFs complexos, escaneados ou tabelas que precisem do modo híbrido:

```bash
opendataloader-pdf-hybrid --port 5002
```

## Validation Scenario 1: Executar a extração primária real

```bash
python3 -m faturama.cli process-invoice \
  --pdf-path "samples/invoice-2026-04.pdf" \
  --user-id demo-user \
  --timezone America/Sao_Paulo
```

**Expected outcome**:

- o comando inicia o workflow oficial;
- o PDF é convertido em artefatos estruturados dentro do runtime, sem depender de sidecars preparados manualmente;
- o resultado retorna `job_id`, contadores de persistência e status observável;
- evidências de execução mostram o caminho oficial de extração e workflow.

Variáveis úteis durante validação:

- `FATURAMA_DB_PATH`
- `FATURAMA_CHECKPOINT_DB_PATH`
- `FATURAMA_ARTIFACT_CACHE_DIR`
- `FATURAMA_OPENDATALOADER_HYBRID_URL`
- `FATURAMA_AGENT_AUTO_APPLY_THRESHOLD`

## Validation Scenario 2: Exercitar revisão assistida e retomada

Após um processamento que abriu pendência:

```bash
python3 -m faturama.cli review-queue --user-id demo-user
```

Escolha um item e resolva:

```bash
python3 -m faturama.cli resolve-review \
  --review-item-id <review_id> \
  --resolution accepted \
  --note "Confirmado após revisão"
```

Reprocesse ou retome o documento:

```bash
python3 -m faturama.cli process-invoice \
  --pdf-path "samples/invoice-2026-04.pdf" \
  --user-id demo-user
```

**Expected outcome**:

- a pendência é rastreada até o caso de revisão correspondente;
- a resolução pode ser reaplicada no próximo processamento do mesmo documento sem reabrir a mesma pendência;
- não há duplicação de entidades canônicas nem de efeitos prévios.

## Validation Scenario 3: Confirmar consultas preservadas

```bash
python3 -m faturama.cli monthly-spend --user-id demo-user --month 2026-04 --format json
python3 -m faturama.cli future-installments --user-id demo-user --month 2026-05 --format json
python3 -m faturama.cli remaining-balance --user-id demo-user --format json
```

**Expected outcome**:

- as consultas continuam respondendo sobre a mesma base canônica;
- valores observados e projetados permanecem semanticamente separados;
- a troca do runtime interno não altera a superfície do usuário.

Consulte os formatos esperados em [contracts/cli.md](./contracts/cli.md).

## Validation Scenario 4: Verificar o fechamento do desvio arquitetural

```bash
python3 -m faturama.cli usage-report --format json
```

**Expected outcome**:

- `LangGraph` aparece como uso real de runtime no workflow principal;
- `OpenDataLoader` aparece como extração primária real do PDF;
- o relatório deixa de tratar ambos apenas como dependência declarada ou naming arquitetural.

## Validation Status

Os cenários centrais desta feature devem ficar cobertos por:

- `tests/unit/` para transições de estado, roteamento e regras de pausa;
- `tests/integration/` para extração real, geração de artefatos, checkpoints e reprocessamento;
- `tests/contract/` para estabilidade da CLI;
- `tests/e2e/test_invoice_pipeline_e2e.py` e regressões correlatas para fluxo ponta a ponta.

Validação executada no checkout atual em `2026-06-27`:

- `python3 -m pytest -q` => `49 passed`
- `python3 -m faturama.cli usage-report --format json` => `critical_deviations=0`

## Test Guidance

- incluir regressão específica contra o comportamento antigo de apenas resolver sidecars locais;
- validar que checkpoints podem ser restaurados sem criar duplicação;
- validar que o ramo assistido por IA só entra quando regras e confiança exigirem;
- validar que `usage-report` reconhece o fechamento do desvio após a implementação.

## Troubleshooting

- falha de extração primária: confirme Java no `PATH` e a escrita no diretório de artefatos
- necessidade de OCR/layout complexo: suba o backend híbrido e configure `FATURAMA_OPENDATALOADER_HYBRID_URL`
- consultas vazias após migração: verifique se os dados antigos foram invalidados e reprocessados no runtime oficial
