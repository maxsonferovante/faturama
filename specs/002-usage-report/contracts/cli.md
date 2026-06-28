# CLI Contract: Relatório de Uso

## Purpose

Definir a superfície inicial da implementação real do relatório no projeto.

## Base Command

```bash
python3 -m faturama.cli usage-report [options]
```

## Command

### `usage-report`

Analisa o uso real dos componentes cobertos pela v1, produz saída operacional e materializa um relatório Markdown.

**Input**:

```text
usage-report [--output-file <path>] [--fix-when-safe] [--format json|table]
```

**Behavior**:

- analisa LangGraph, OpenDataLoader e sinais estruturais centrais do pipeline atual;
- coleta evidências de uso executável, testes reforçadores e dependências declaradas;
- classifica cada alvo no escopo;
- identifica desvios entre comportamento observado e expectativa declarada;
- quando `--fix-when-safe` estiver ativo, aplica correções apenas se houver contexto suficiente e rastreável;
- materializa um arquivo Markdown com o mesmo diagnóstico.

**Output shape**:

```json
{
  "report_id": "string",
  "targets_analyzed": 0,
  "findings": 0,
  "critical_deviations": 0,
  "auto_fixes_applied": 0,
  "manual_followups": 0,
  "operational_metrics": {
    "targets_analyzed": 0,
    "critical_deviations": 0,
    "auto_fixes_applied": 0,
    "manual_followups": 0
  },
  "markdown_output_path": "string"
}
```

## Classification Contract

Cada alvo analisado deve cair em uma das classificações:

- `used_in_runtime`
- `declared_not_used`
- `conceptual_only`
- `insufficient_context`

## Error Contract

- código de saída `0` quando a análise completa sem erro operacional;
- código diferente de `0` quando a execução falha estruturalmente;
- desvios críticos sem correção automática segura não são erro estrutural por si só, mas devem aparecer na saída e no Markdown.

## Operational Signals

Cada execução bem-sucedida deve registrar, no mínimo:

- contagem de alvos analisados;
- contagem de desvios críticos;
- contagem de correções aplicadas;
- contagem de follow-ups manuais.

## Materialized Markdown Expectations

O arquivo materializado deve conter, no mínimo:

- resumo executivo;
- lista de alvos analisados;
- evidências por alvo;
- desvios identificados;
- correções aplicadas;
- pendências manuais.
