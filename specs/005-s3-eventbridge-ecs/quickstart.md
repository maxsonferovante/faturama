# Quickstart: S3 EventBridge ECS

## Objective

Validar localmente que um upload real de PDF no bucket de entrada dispara uma task ECS sob demanda a partir de um evento do S3 roteado pelo EventBridge, sem fila intermediária, lambda bridge ou Step Functions.

## Prerequisites

- Docker e Docker Compose disponíveis no ambiente
- Terraform disponível no `PATH`
- Python 3.12+ e `uv` disponíveis para rodar o script de teste
- imagem local `faturama-worker:local` construída pelo bootstrap
- PDF de teste acessível no host

## Setup

Suba o ambiente local:

```bash
bash scripts/bootstrap_local_runtime.sh
```

O bootstrap deve:

1. subir `postgres` e `ministack`;
2. construir `faturama-worker:local`;
3. inicializar e validar o Terraform local;
4. aplicar a infraestrutura do runtime;
5. deixar buckets, regra EventBridge, cluster ECS e task definition prontos.

## Validation Scenario 1: Confirmar provisionamento mínimo

```bash
terraform -chdir=infra/terraform/environments/local output
```

**Expected outcome**:

- bucket de entrada disponível;
- bucket de artefatos disponível;
- regra de dispatch do EventBridge criada;
- cluster ECS criado;
- task definition do worker publicada;
- ausência de dependência operacional de fila, lambda ou state machine no caminho principal.

## Validation Scenario 2: Enviar PDF e observar dispatch real

Edite o bloco `TEST_CONFIG` do script [scripts/test_worker_from_ministack_s3.py](/Users/USER_PROFILE/Documents/faturama/scripts/test_worker_from_ministack_s3.py) com o PDF desejado e execute:

```bash
uv run scripts/test_worker_from_ministack_s3.py
```

**Expected outcome**:

- o script envia o PDF ao bucket `pre-processamento-faturama`;
- nenhuma chamada local direta ao worker é feita pelo script;
- uma task/container real do worker aparece após o upload;
- o script consegue observar artefatos no bucket `processados-faturama`.

**Observed on MiniStack `1.3.69` (`ministackorg/ministack:full`, image created on 2026-06-27)**:

- a regra EventBridge e o target ECS sao provisionados corretamente;
- o upload chega ao bucket S3 local;
- durante a espera do teste real nao apareceu container ECS nem artefato novo;
- um `put_events` manual contra o EventBridge local retorna a evidência `EventBridge: unsupported target type for ARN arn:aws:ecs:...:cluster/faturama-cluster`;
- portanto o dispatch real para ECS nao acontece nesse runtime local.

## Validation Scenario 3: Verificar evidência operacional

Use os sinais abaixo para confirmar o caminho real:

- transição de um container `ministack-ecs-...-worker` após o upload;
- artefatos novos sob o prefixo `processed/` no bucket de saída;
- ausência de necessidade de execução Step Functions para o fluxo acontecer.

## Validation Scenario 4: Regressão funcional mínima

```bash
python3 -m pytest tests/contract tests/integration tests/e2e -q
```

**Expected outcome**:

- o contrato `ProcessingCommand` continua válido;
- o worker continua lendo do S3 e persistindo artefatos e status;
- o fluxo assíncrono não depende mais de recursos removidos do desenho anterior.

## Troubleshooting

- upload sem dispatch: revisar pattern da regra EventBridge, bucket configurado e prefixo/sufixo elegíveis;
- dispatch sem task ECS: revisar permissões `ecs:RunTask` e `iam:PassRole` da role usada pelo EventBridge;
- dispatch sem task ECS com log `unsupported target type for ARN arn:aws:ecs:...:cluster/...`: limitacao atual do MiniStack, nao erro do Terraform da feature;
- task inicia mas não processa: revisar `FATURAMA_PROCESSING_MESSAGE`, endpoint AWS local e acesso do task role ao S3;
- artefatos ausentes: revisar bucket de saída, prefixo de artefatos e logs do container do worker;
- bootstrap incompleto: revisar `terraform validate`, imports de buckets existentes e compatibilidade do endpoint local.
