# Contract: Runtime Config

## Objective

Definir a configuração mínima necessária para que o runtime `S3 -> EventBridge -> ECS` funcione de forma consistente entre ambiente local e AWS.

## Required Runtime Inputs

### Worker container

- `FATURAMA_RUNTIME_ENV`
- `FATURAMA_DB_DSN`
- `FATURAMA_AWS_REGION`
- `FATURAMA_INPUT_BUCKET`
- `FATURAMA_ARTIFACT_BUCKET`
- `FATURAMA_ARTIFACT_PREFIX`
- `FATURAMA_SIGNED_UPLOAD_EXPIRATION_SECONDS`
- `FATURAMA_AWS_ENDPOINT_URL` no ambiente local compatível
- `FATURAMA_PROCESSING_MESSAGE` fornecida pelo dispatch EventBridge -> ECS

### Terraform module inputs

- `aws_region`
- `environment_name`
- `input_bucket_name`
- `artifact_bucket_name`
- `artifact_prefix`
- `ecs_cluster_name`
- `ecs_task_family`
- `container_image_uri`
- `db_name`
- `db_username`
- `db_password`
- `db_host`
- `db_port`
- `use_local_aws_endpoints`
- `local_aws_endpoint_url`
- `local_container_aws_endpoint_url`
- `subnet_ids`
- `security_group_ids`
- `log_group_name`

## Removed Terraform Inputs

Os seguintes inputs deixam de fazer parte do contrato alvo desta feature:

- `processing_queue_name`
- `processing_dlq_name`
- `pipe_name`
- `state_machine_name`
- `status_polling_visibility_seconds`

## Expected Outputs

O módulo Terraform deve continuar expondo, no mínimo:

- nome do bucket de entrada;
- nome do bucket de artefatos;
- nome e ARN do cluster ECS;
- ARN da task definition do worker;
- nome e ARN da regra de dispatch do EventBridge.

## Local Validation Contract

O bootstrap local deve:

1. subir `postgres` e `ministack` via Docker Compose;
2. construir a imagem `faturama-worker:local`;
3. executar `terraform init`, `terraform validate` e `terraform apply`;
4. deixar o ambiente pronto para um teste que apenas envia um PDF ao bucket de entrada e observa a execução assíncrona real.

## Current Emulator Limitation

No ambiente local atual com `ministackorg/ministack:full` `1.3.69`, o Terraform consegue criar a regra EventBridge e o target ECS, mas a validacao local mostrou duas limitacoes:

- o upload real no S3 local nao gerou evidência suficiente de entrega ate o ECS;
- quando um evento e publicado manualmente no EventBridge, o emulador nao executa o target ECS.

A evidência operacional observada no container do MiniStack é:

```text
EventBridge: unsupported target type for ARN arn:aws:ecs:us-east-1:000000000000:cluster/faturama-cluster
```

Essa limitacao afeta a validacao ponta a ponta local, mas nao altera o contrato Terraform/AWS alvo da feature.
