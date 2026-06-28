# Quickstart: Relatório de Uso

## Objective

Validar a feature ponta a ponta como implementação real no projeto.

## Prerequisites

- checkout local do repositório
- dependências Python instaladas
- árvore de código atual disponível para leitura

## Scenario 1: Gerar diagnóstico operacional

```bash
python3 -m faturama.cli usage-report --format json
```

**Expected outcome**:

- a execução retorna um resumo do diagnóstico;
- LangGraph, OpenDataLoader e sinais estruturais centrais entram no escopo;
- cada alvo recebe classificação explícita e evidência associada;
- a saída inclui contagens operacionais mínimas da execução;
- um arquivo Markdown é materializado com o mesmo conteúdo essencial.

## Scenario 2: Materializar relatório em caminho explícito

```bash
python3 -m faturama.cli usage-report --output-file docs/usage-report.md
```

**Expected outcome**:

- o relatório é salvo no caminho informado;
- a saída operacional informa o local materializado;
- o conteúdo permanece consistente entre CLI e Markdown.

## Scenario 3: Corrigir desvio quando seguro

```bash
python3 -m faturama.cli usage-report --fix-when-safe --format json
```

**Expected outcome**:

- desvios críticos com contexto suficiente são corrigidos no mesmo fluxo;
- o resultado informa quantas correções foram aplicadas;
- desvios sem contexto suficiente permanecem registrados como follow-up manual.

## Scenario 4: Validar legibilidade do relatório

```bash
python3 -m faturama.cli usage-report --output-file docs/usage-report.md
```

**Expected outcome**:

- o Markdown materializado contém resumo executivo, alvos analisados, evidências, desvios e ações;
- um mantenedor consegue localizar os itens críticos sem ler o arquivo inteiro.

## Validation Notes

- use o contrato em [contracts/cli.md](./contracts/cli.md) para validar o shape de saída;
- use o modelo em [data-model.md](./data-model.md) para verificar consistência de entidades e transições;
- a suíte da feature deve incluir testes unitários, integração, contrato de CLI e e2e.

## Execution Record

Validação executada no checkout atual em `2026-06-27`:

- `python3 -m faturama.cli usage-report --format json`
- `python3 -m faturama.cli usage-report --fix-when-safe --format table`
- suíte da feature `usage-report`: `22 passed`

Resultado observado no repositório atual:

- `targets_analyzed=4`
- `critical_deviations=2`
- `auto_fixes_applied=0`
- `manual_followups=2`
- arquivo materializado em `docs/reports/usage-report.md`

Os desvios críticos observados no estado atual foram:

- `LangGraph` declarado como dependência/arquitetura, sem integração real de runtime;
- `OpenDataLoader` declarado como extrator primário, mas o runtime atual ainda opera por sidecars locais.
