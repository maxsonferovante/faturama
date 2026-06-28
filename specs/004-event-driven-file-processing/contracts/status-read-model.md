# Contract: Status Read Model

## Purpose

Definir a visão persistida que outra API do contexto maior deve consultar para acompanhar o processamento assíncrono.

## Contract Owner

- produtor: worker assíncrono e componentes que atualizam o ledger de processamento
- consumidor: API externa de status apoiada no banco de dados

## Canonical Fields

```json
{
  "processing_id": "evt-20260628-0001",
  "document_id": "doc-123",
  "file_hash": "sha256...",
  "status": "RUNNING",
  "is_terminal": false,
  "review_required": false,
  "status_detail": "extraindo documento",
  "result_reference": null,
  "artifact_manifest_id": null,
  "last_transition_at": "2026-06-28T12:01:12Z",
  "updated_at": "2026-06-28T12:01:12Z"
}
```

## Required Rules

- a API de status deve consultar esta visão persistida, não o runtime da task ECS;
- `processing_id` identifica a tentativa operacional exibida ao consumidor;
- `file_hash` representa a identidade canônica do documento e pode aparecer em múltiplas tentativas;
- `status` deve suportar no mínimo `PENDING`, `RUNNING`, `REVIEW_REQUIRED`, `SUCCESS`, `PARTIAL`, `FAILED`;
- `REVIEW_REQUIRED` deve ser tratado como não terminal;
- `result_reference` só deve ser preenchido quando já existir resultado canônico persistido ou artefato final consultável.
- `artifact_manifest_id` deve apontar para o manifesto persistido dos artefatos OpenDataLoader quando esses arquivos existirem.

## Query Semantics

- consultas por `processing_id` devem retornar exatamente uma visão ativa da tentativa;
- múltiplas tentativas para o mesmo `file_hash` podem coexistir, desde que a API deixe claro qual tentativa está sendo consultada;
- estados terminais devem permanecer visíveis para auditoria e reprocessamento controlado;
- a API leitora não deve inferir sucesso a partir da ausência de erro; ela deve confiar no `status` persistido.
