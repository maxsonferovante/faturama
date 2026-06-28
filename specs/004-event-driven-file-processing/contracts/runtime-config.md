# Contract: Runtime Configuration

## Purpose

Definir a configuração mínima que precisa permanecer estável entre desenvolvimento local, AWS de desenvolvimento, homologação e produção.

## Application Runtime Variables

```text
FATURAMA_RUNTIME_ENV
FATURAMA_AWS_REGION
FATURAMA_AWS_ENDPOINT_URL
FATURAMA_INPUT_BUCKET
FATURAMA_ARTIFACT_BUCKET
FATURAMA_ARTIFACT_PREFIX
FATURAMA_PROCESSING_MESSAGE
FATURAMA_DB_DSN
FATURAMA_LOG_LEVEL
FATURAMA_SIGNED_UPLOAD_EXPIRATION_SECONDS
FATURAMA_CONFIDENCE_THRESHOLD
FATURAMA_AGENT_AUTO_APPLY_THRESHOLD
FATURAMA_OPENDATALOADER_HYBRID_URL
```

## Infrastructure Variables

```text
aws_region
environment_name
input_bucket_name
artifact_bucket_name
artifact_prefix
signed_upload_expiration_seconds
processing_queue_name
processing_dlq_name
pipe_name
state_machine_name
ecs_cluster_name
ecs_task_family
container_image_uri
db_name
db_username
db_password_secret_ref
db_host
db_port
status_polling_visibility_seconds
use_local_aws_endpoints
local_aws_endpoint_url
subnet_ids
security_group_ids
log_group_name
```

## Configuration Rules

- nomes de recursos devem ser equivalentes entre ambiente local e AWS real, mudando apenas sufixos de ambiente quando necessário;
- `FATURAMA_AWS_ENDPOINT_URL` e `local_aws_endpoint_url` só devem ser preenchidos em ambientes locais;
- `FATURAMA_DB_DSN` deve apontar para PostgreSQL em todos os ambientes do fluxo assíncrono;
- `FATURAMA_ARTIFACT_BUCKET` deve apontar para `processados-faturama` na v1;
- `FATURAMA_SIGNED_UPLOAD_EXPIRATION_SECONDS` deve controlar a janela de uso das URLs assinadas emitidas para integradores externos;
- segredos de banco e credenciais sensíveis não podem ficar hardcoded no código-fonte nem em arquivos versionados;
- o worker deve conseguir operar apenas com as variáveis obrigatórias e o contrato `FATURAMA_PROCESSING_MESSAGE`.

## Local Parity Notes

- o ambiente local deve provisionar recursos AWS compatíveis via Terraform apontando para o endpoint local;
- o banco local pode ser PostgreSQL em container dedicado, desde que o DSN preserve o contrato esperado pelo worker;
- qualquer lacuna de emulação para CloudWatch Logs deve ter fallback operacional explícito para validação local por stdout e inspeção de container;
- diferenças inevitáveis entre local e AWS real devem ser tratadas como documentação de paridade, não como contratos divergentes de payload ou nomes de recursos.
