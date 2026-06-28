# Runbook: Usage Report

## Objetivo

Gerar um diagnostico operacional do uso real de LangGraph, OpenDataLoader e sinais estruturais centrais do pipeline atual, com saida por CLI e materializacao em Markdown.

## Comando base

```bash
python3 -m faturama.cli usage-report --format json
```

## Convencao de materializacao

- caminho padrao: `docs/reports/usage-report.md`
- caminho customizado: `--output-file <path>`
- o comando cria diretorios pais ausentes automaticamente
- se o caminho informado nao puder ser criado, a CLI retorna erro estrutural com `error_code=usage_report_failed`

## Modos uteis

```bash
python3 -m faturama.cli usage-report --format table
python3 -m faturama.cli usage-report --output-file docs/usage-report.md
python3 -m faturama.cli usage-report --fix-when-safe --format json
```

## Semantica operacional

- `targets_analyzed`: quantos alvos do escopo foram inspecionados
- `critical_deviations`: quantos desvios materiais e criticos foram encontrados
- `auto_fixes_applied`: quantas correcoes seguras foram aplicadas no mesmo fluxo
- `manual_followups`: quantos casos exigem acao manual

## Leitura do resultado

- `used_in_runtime`: ha evidencia executavel de uso real
- `declared_not_used`: a integracao permanece como dependencia declarada ou promessa arquitetural
- `conceptual_only`: ha apenas naming, estrutura ou documentacao
- `insufficient_context`: a base observada nao permite conclusao forte

## Resultado validado no checkout atual

Execucao validada em `2026-06-27`:

- `python3 -m faturama.cli usage-report --format json`
- `python3 -m faturama.cli usage-report --fix-when-safe --format table`

Resumo observado:

- `targets_analyzed=4`
- `critical_deviations=0`
- `auto_fixes_applied=0`
- `manual_followups=0`

No estado atual do projeto, o relatorio aponta:

- `LangGraph` como uso real de runtime no workflow principal e no checkpointer SQLite
- `OpenDataLoader` como extracao primaria real do PDF e `OpenDataLoaderPDFLoader` como loader do ramo assistido
- checkpoints, cache de artefatos e consultas canonicas alinhados sem desvios criticos abertos

## Troubleshooting

- saida muito grande em JSON: use `--format table` para leitura rapida
- resultado materializado inesperado: abra `docs/reports/usage-report.md` e confira a secao de evidencias
- falso positivo local em testes: confira `FATURAMA_USAGE_REPORT_ROOT` antes de executar a CLI
