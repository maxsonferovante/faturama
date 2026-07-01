# Faturama

Pipeline local para extracao auditavel de faturas de cartao, persistencia em PostgreSQL e consultas por CLI, com runtime assíncrono provisionado por Terraform para dispatch `S3 -> EventBridge -> ECS`.

## Stack

- Python com estrutura `src/`
- Persistencia PostgreSQL única para dados e checkpoints
- Contratos Pydantic
- `LangGraph` como workflow oficial
- `OpenDataLoader PDF` como extracao primaria de PDF
- Suite `pytest` cobrindo contrato, integracao, unidade e e2e

## Comandos principais

```bash
python3 -m faturama.cli process-invoice --pdf-path samples/invoice-2026-04.pdf --user-id demo-user
python3 -m faturama.cli monthly-spend --user-id demo-user --month 2026-04
python3 -m faturama.cli future-installments --user-id demo-user --month 2026-05
python3 -m faturama.cli review-queue --user-id demo-user
faturama-worker --help-message
```

## Variaveis uteis

- `FATURAMA_DB_DSN`
- `FATURAMA_ARTIFACT_CACHE_DIR`
- `FATURAMA_INPUT_BUCKET`
- `FATURAMA_ARTIFACT_BUCKET`
- `FATURAMA_PROCESSING_MESSAGE`
- `FATURAMA_AWS_ENDPOINT_URL`

## Runtime local assincrono

No ambiente local, o runtime sobe com `postgres`, `ministack`, imagem Docker do worker e infraestrutura Terraform. O fluxo alvo e:

1. upload do PDF em `pre-processamento-faturama`
2. evento `Object Created` do S3
3. regra EventBridge
4. `ecs:RunTask`
5. worker real processando o PDF
6. artefatos gravados em `processados-faturama`

Suba tudo com:

```bash
bash scripts/bootstrap_local_runtime.sh
```

Esse script faz, em ordem:

1. sobe `postgres` e `ministack` pelo `docker compose`
2. builda a imagem local `faturama-worker:local`
3. executa `terraform init`, `terraform validate` e `terraform apply`
4. provisiona buckets S3, habilitacao do EventBridge no bucket de entrada, regra EventBridge, ECS e IAM

Se a porta `4566` ja estiver ocupada:

```bash
MINISTACK_PORT=4567 bash scripts/bootstrap_local_runtime.sh
```

Para conferir os recursos provisionados:

```bash
terraform -chdir=infra/terraform/environments/local output
```

O output esperado inclui ao menos:

- bucket de entrada `pre-processamento-faturama`
- bucket de artefatos `processados-faturama`
- regra `faturama-processing-dispatch`
- cluster ECS `faturama-cluster`

## Teste real via S3 do MiniStack

O teste real do fluxo assíncrono é o script [scripts/test_worker_from_ministack_s3.py](/Users/USER_PROFILE/Documents/faturama/scripts/test_worker_from_ministack_s3.py).

Ele faz somente a entrada do fluxo: envia um PDF ao bucket S3. O restante precisa acontecer pela infraestrutura provisionada.

Antes de rodar, edite apenas o bloco `TEST_CONFIG` no topo do script. Exemplo:

```python
TEST_CONFIG = {
    "pdf_path": "/Users/USER_PROFILE/Documents/faturama/refinamento-faturama/faturajunhointer.pdf",
    "object_key": "incoming/faturajunhointer.pdf",
    "endpoint_url": "http://localhost:4566",
    "aws_region": "us-east-1",
    "input_bucket": "pre-processamento-faturama",
    "artifact_bucket": "processados-faturama",
    "artifact_prefix": "processed",
    "dispatch_rule_name": "faturama-processing-dispatch",
    "wait_timeout_seconds": 180,
    "poll_interval_seconds": 5,
    "worker_image": "faturama-worker:local",
    "ministack_container_name": "faturama-ministack-1",
    "show_docker_progress": True,
}
```

Depois execute:

```bash
uv run scripts/test_worker_from_ministack_s3.py
```

## Como acompanhar a execucao

O script ja mostra progresso em tempo real. Os sinais importantes sao:

- linha `enviando ... para s3://pre-processamento-faturama/...`
- linha `aguardando processamento real via S3 -> EventBridge -> ECS`
- aparicao de `container novo ...`
- transicoes de status do container `ministack-ecs-...-worker`
- logs recentes do container do worker
- linhas `artifact processed/...`
- JSON final com `status: "ok"`

Se o runtime local nao suportar o target ECS do EventBridge, o script agora encerra cedo com `status: "unsupported_runtime"` e inclui a linha de log do MiniStack que prova a limitacao.

Se quiser acompanhar por fora do script:

```bash
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}'
```

```bash
terraform -chdir=infra/terraform/environments/local output
```

## Resultado esperado

Quando tudo estiver correto, o worker termina com `Exited (0)` e o JSON final do script mostra:

- pelo menos um container novo do worker
- artefatos no bucket `processados-faturama`
- `pdf`, `md`, `json` e `result.json`

Exemplo de chaves geradas:

```text
processed/<processing-id>/<pdf-stem>-<hash>/<pdf-stem>.pdf
processed/<processing-id>/<pdf-stem>-<hash>/<pdf-stem>.md
processed/<processing-id>/<pdf-stem>-<hash>/<pdf-stem>.json
processed/<processing-id>/<pdf-stem>-<hash>/<pdf-stem>-result.json
```

## Matriz de validacao atual

Em `2026-06-28`, a validacao executada neste repositorio ficou assim:

| Etapa                    | Comando                                                                                                                                                  | Resultado                                                                                                           |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Terraform estatico       | `terraform -chdir=infra/terraform/environments/local validate`                                                                                           | PASS                                                                                                                |
| Provisionamento local    | `bash scripts/bootstrap_local_runtime.sh`                                                                                                                | PASS                                                                                                                |
| Contratos e wiring local | `python3 -m pytest tests/contract/test_processing_message_contract.py tests/integration/test_async_dispatch.py tests/e2e/test_local_runtime_contract.py` | PASS                                                                                                                |
| Dispatch real por upload | `uv run scripts/test_worker_from_ministack_s3.py`                                                                                                        | FAIL por timeout: nenhum container ECS nem artefato novo apareceu apos o upload                                      |
| Isolamento manual do target ECS | `put_events` manual no EventBridge local | FAIL no MiniStack `1.3.69`: `EventBridge: unsupported target type for ARN arn:aws:ecs:...:cluster/faturama-cluster` |

Isso significa:

- o Terraform do desenho novo esta correto e provisiona buckets, regra e target;
- o upload chega ao S3 local;
- o upload S3 local nao mostrou evidencia de entrega ate o target ECS durante a janela do teste;
- quando o EventBridge recebe um evento manualmente, a versao atual do MiniStack usada em `ministackorg/ministack:full` ainda nao executa target ECS do EventBridge;
- por isso o fluxo `S3 -> EventBridge -> ECS` fica pronto para AWS real, mas nao fecha o e2e completo nesse emulador especifico.

## Validacao

```bash
bash scripts/bootstrap_local_runtime.sh
python3 -m pytest -q
uv run scripts/test_worker_from_ministack_s3.py
```
