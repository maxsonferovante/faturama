# Quickstart: Processamento Assincrono de Faturas por Eventos

## Objective

Validar localmente que um upload de PDF por URL assinada dispara o fluxo assíncrono completo, inicia uma task ECS sob demanda, persiste status em PostgreSQL e deixa esse estado disponível para a API de consulta baseada em banco, preservando o comportamento funcional do pipeline existente.

## Prerequisites

- Docker e Docker Compose disponíveis no ambiente
- Terraform disponível no `PATH`
- Python 3.12+ para comandos auxiliares e testes do repositório
- imagem Docker do worker construída localmente
- um PostgreSQL compatível disponível na composição local
- PDF de amostra acessível no repositório

## Suggested Local Setup

Suba o ambiente local:

```bash
docker compose up -d
```

Provisione a infraestrutura local:

```bash
terraform -chdir=infra/terraform/environments/local init -backend=false
terraform -chdir=infra/terraform/environments/local apply
```

Construa a imagem do worker:

```bash
docker build -f docker/worker/Dockerfile -t faturama-worker:local .
```

## Validation Scenario 1: Provisionamento e paridade básica

Verifique se o ambiente local criou os recursos mínimos esperados:

```bash
terraform -chdir=infra/terraform/environments/local output
```

**Expected outcome**:

- bucket `pre-processamento-faturama` disponível;
- fila principal e DLQ configuradas;
- pipe e state machine provisionados;
- cluster ECS e task definition publicados;
- PostgreSQL acessível pelo DSN configurado para o worker.

## Validation Scenario 2: Upload dispara dispatch assíncrono

Obtenha uma URL assinada do emissor local do ambiente e envie um PDF de exemplo:

```bash
curl -X PUT -T samples/invoice-2026-04.pdf "<URL_ASSINADA>"
```

**Expected outcome**:

- o upload retorna imediatamente para o operador;
- a fila recebe a mensagem e a encaminha para a Step Function pelo pipe;
- a Step Function cria um `processing_id` e dispara a task ECS sem esperar o término;
- o ledger de processamento registra `PENDING` e depois `RUNNING`.

Consulte os formatos esperados em [contracts/signed-upload.md](./contracts/signed-upload.md), [contracts/processing-message.md](./contracts/processing-message.md) e [contracts/orchestration.md](./contracts/orchestration.md).

## Validation Scenario 3: Consulta de status, revisão e idempotência

Consulte o read model de status pela API do contexto maior:

```bash
curl "<STATUS_API>/<processing_id>"
```

Reenvie o mesmo arquivo para validar idempotência operacional:

```bash
curl -X PUT -T samples/invoice-2026-04.pdf "<URL_ASSINADA_DE_RETRY>"
```

**Expected outcome**:

- a API de status expõe `RUNNING`, `REVIEW_REQUIRED`, `SUCCESS`, `PARTIAL` ou `FAILED` sem depender de evento externo de conclusão;
- `REVIEW_REQUIRED` permanece pendente até retomada ou resolução;
- o primeiro envio chega a `SUCCESS`, `REVIEW_REQUIRED` ou `PARTIAL` com contexto suficiente para diagnóstico;
- os artefatos OpenDataLoader ficam gravados em `processados-faturama` com chave rastreável e referência persistida no banco;
- o reenvio não duplica entidades canônicas já persistidas para o mesmo documento;
- a fila de revisão e os checkpoints seguem rastreáveis no armazenamento durável quando houver ambiguidade.

Para cobertura automatizada:

```bash
python3 -m pytest tests/e2e -q
```

## Observability Checks

Preferencialmente em AWS real, validar logs centralizados do worker e da state machine. No ambiente local:

- use a trilha do `processing_id` para correlacionar dispatch, execução e persistência;
- consulte logs centralizados se a emulação local suportar o recurso;
- quando a criação de log groups não estiver plenamente emulada, valide por stdout e logs do container sem alterar o contrato do worker.

## Validation Status

Os cenários desta feature devem ficar cobertos por:

- `tests/unit/` para normalização de payload, idempotência e transições de estado;
- `tests/contract/` para o contrato do `ProcessingCommand`, da URL assinada e do read model de status;
- `tests/integration/` para adapters S3/PostgreSQL, persistência de checkpoints e manifesto dos artefatos processados;
- `tests/e2e/` para o fluxo completo `upload -> queue -> state machine -> ecs -> postgres`.

## Troubleshooting

- dispatch não iniciado: verificar prefixo/sufixo da notificação S3, política do bucket e saúde do pipe;
- upload rejeitado: verificar expiração da URL assinada, chave autorizada e método `PUT`;
- Step Function sem task ECS: revisar permissões `ecs:RunTask` e `iam:PassRole`;
- worker falha ao baixar PDF: revisar endpoint AWS configurado, bucket e chave normalizada;
- artefato ausente em `processados-faturama`: revisar permissões de escrita no bucket de processados, geração da chave rastreável e persistência do manifesto no banco;
- status preso em `RUNNING`: inspecionar logs do container, checkpoints, conectividade com PostgreSQL e atualização do read model consultado pela API;
- ausência de logs centralizados no local: confirmar diferença documentada de paridade antes de assumir defeito do fluxo principal.
