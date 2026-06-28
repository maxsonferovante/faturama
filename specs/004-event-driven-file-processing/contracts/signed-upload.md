# Contract: Signed Upload

## Purpose

Definir o contrato funcional entre o emissor de URL assinada do contexto maior e o bucket de entrada usado pelo processamento assíncrono.

## Contract Owner

- emissor lógico: API externa de ingestão do contexto maior
- consumidor imediato: cliente integrador que fará o `PUT`
- efeito esperado nesta feature: geração de um objeto elegível no bucket `pre-processamento-faturama`

## Contract Rules

- a URL assinada deve autorizar apenas `PUT`;
- a URL assinada deve apontar para uma chave específica e previamente autorizada;
- a URL assinada deve ter expiração limitada e explícita;
- o upload bem-sucedido deve ser correlacionável a um `upload_grant_id`;
- o upload não deve exigir credenciais AWS permanentes do cliente integrador.

## Minimal Grant Shape

```json
{
  "upload_grant_id": "grant-20260628-001",
  "bucket": "pre-processamento-faturama",
  "object_key": "incoming/invoice-2026-04.pdf",
  "method": "PUT",
  "expires_at": "2026-06-28T12:05:00Z",
  "presigned_url": "https://..."
}
```

## Validation Semantics

- se o upload ocorrer após `expires_at`, ele deve ser rejeitado;
- se o cliente tentar gravar em chave diferente da autorizada, o upload deve ser rejeitado;
- se o mesmo object key já existir, o comportamento deve ser tratado como nova tentativa operacional e depender da deduplicação canônica posterior por hash do PDF;
- após o upload bem-sucedido, o objeto fica sob propriedade operacional do ambiente processador.
