# Runbook: Performance Validation

## Metas da v1

- processar uma fatura suportada em menos de 60s
- responder consultas persistidas em menos de 5s

## Como validar

```bash
python3 -m pytest tests/integration/test_processing_performance.py -q
python3 -m pytest tests/integration/test_query_performance.py -q
```

## Cenarios cobertos

- ingestao completa de uma fatura pelo workflow `LangGraph`
- geração/reuso de artefatos do `OpenDataLoader`
- consulta `monthly-spend` sobre base ja persistida

## Interpretacao

- falha em processamento: revisar IO, custo do `OpenDataLoader`, checkpoints e parsing excessivo
- falha em consulta: revisar indices, estrategia de agregacao e custo de reprocessamento

## Limites atuais

- os testes usam fixtures pequenas e o modo stub para isolar o contrato operacional minimo
- emissores adicionais e OCR pesado devem ser reavaliados com massa real
