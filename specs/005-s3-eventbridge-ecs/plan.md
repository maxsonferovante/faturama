# Implementation Plan: S3 EventBridge ECS

**Branch**: `[]` | **Date**: 2026-06-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-s3-eventbridge-ecs/spec.md`

## Summary

Redesenhar o runtime assíncrono para usar `S3 -> EventBridge -> ECS RunTask` como caminho principal de dispatch, removendo SQS, Lambda bridge, EventBridge Pipe e Step Functions do módulo Terraform, preservando o worker atual, a persistência em PostgreSQL, os buckets de entrada/artefatos e a validação ponta a ponta por upload real no ambiente local.

## Technical Context

**Language/Version**: Python 3.12+ para a aplicação e scripts; Terraform HCL para infraestrutura; Bash para bootstrap local existente

**Primary Dependencies**: `boto3`, `pydantic`, runtime atual do worker em `src/faturama/interface/worker`, provider `hashicorp/aws`, provider `hashicorp/archive` a ser removido se não houver mais artefatos Lambda, Docker Compose

**Storage**: Amazon S3 compatível para bucket de entrada `pre-processamento-faturama` e bucket de artefatos `processados-faturama`; PostgreSQL para status, ledger operacional e manifesto de artefatos

**Testing**: `pytest`, `terraform validate`, `scripts/bootstrap_local_runtime.sh`, `scripts/test_worker_from_ministack_s3.py` atualizado para observar o fluxo real `upload -> EventBridge -> ECS -> artefatos`

**Target Platform**: ECS task sob demanda em AWS e ambiente local compatível via MiniStack + Docker

**Project Type**: backend Python orientado a workflow com infraestrutura como código

**Performance Goals**: iniciar o dispatch em até 30 segundos após `Object Created`; concluir PDFs válidos em até 5 minutos no fluxo local de referência; manter evidência operacional suficiente para diagnosticar falhas sem componentes intermediários

**Constraints**: toda a infraestrutura local deve ser criada via Terraform; o teste ponta a ponta não pode invocar o worker localmente; o fluxo deve evitar loops de evento; o bucket de saída não pode disparar novo processamento; a solução deve continuar usando `boto3` e os adapters reais da aplicação

**Scale/Scope**: um bucket de entrada, um bucket de artefatos, uma regra EventBridge, um target ECS RunTask, um cluster ECS e um worker container; suporte mínimo à validação com burst de 20 uploads elegíveis na v1

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Pythonic Correctness and Readability`: PASS. O desenho preserva o worker Python existente e concentra a mudança na borda de infraestrutura e nos contratos de mensagem.
- `Clean Architecture Boundaries`: PASS. EventBridge, ECS, S3 e Terraform permanecem em infraestrutura; o domínio e a aplicação continuam consumindo um `ProcessingCommand` estável.
- `Object-Oriented Design and SOLID`: PASS. O redesenho remove camadas intermediárias em vez de adicionar novas abstrações, reduzindo responsabilidades espalhadas entre fila, lambda e state machine.
- `Testable Design and Quality Gates`: PASS. O plano exige `terraform validate`, ajuste do bootstrap e teste ponta a ponta por upload real sem invocação local do worker.
- `Simplicity, Observability, and Operational Reliability`: PASS. A arquitetura alvo reduz componentes no caminho crítico, mantém logs/evidências operacionais e usa filtros precisos no EventBridge para evitar loops e matches indevidos.

## Project Structure

### Documentation (this feature)

```text
specs/005-s3-eventbridge-ecs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── orchestration.md
│   ├── processing-message.md
│   └── runtime-config.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── faturama/
    ├── application/
    ├── infrastructure/
    ├── interface/
    │   └── worker/
    └── observability/

infra/
└── terraform/
    ├── modules/
    │   └── faturama_runtime/
    └── environments/
        ├── aws/
        └── local/

scripts/
├── bootstrap_local_runtime.sh
└── test_worker_from_ministack_s3.py

tests/
├── contract/
├── e2e/
├── integration/
└── unit/
```

**Structure Decision**: A mudança fica concentrada no módulo Terraform `infra/terraform/modules/faturama_runtime`, nas composições dos ambientes `infra/terraform/environments/{local,aws}`, no script de bootstrap, no teste ponta a ponta real e na eventual normalização do contrato de evento no worker. O núcleo Python de processamento permanece intacto, consumindo um `ProcessingCommand` estável.

## Phase 0: Research Summary

As decisões de pesquisa foram consolidadas em [research.md](./research.md) com foco em: usar eventos diretos do Amazon S3 no EventBridge, direcionar a regra do EventBridge diretamente para `ecs:RunTask`, derivar o identificador da tentativa a partir do envelope do evento, manter filtros precisos de bucket/prefixo/sufixo para evitar loops, simplificar o módulo Terraform removendo recursos intermediários e validar o fluxo local com upload real e observação assíncrona da execução ECS.

## Phase 1: Design Summary

- O modelo de dados operacional do dispatch simplificado foi definido em [data-model.md](./data-model.md).
- Os contratos de orquestração, mensagem de processamento e configuração de runtime foram definidos em [contracts/orchestration.md](./contracts/orchestration.md), [contracts/processing-message.md](./contracts/processing-message.md) e [contracts/runtime-config.md](./contracts/runtime-config.md).
- O guia de validação local foi documentado em [quickstart.md](./quickstart.md), cobrindo bootstrap via Terraform, upload real para S3, observação do disparo do ECS e checagem dos artefatos de saída.
- O bloco gerenciado do agente deve apontar para este plano após a atualização de contexto.

## Post-Design Constitution Check

- `Pythonic Correctness and Readability`: PASS. O design mantém contratos explícitos e reduz o acoplamento estrutural do fluxo assíncrono.
- `Clean Architecture Boundaries`: PASS. Os detalhes de S3/EventBridge/ECS continuam encapsulados em infraestrutura e scripts operacionais.
- `Object-Oriented Design and SOLID`: PASS. O desenho elimina responsabilidades transitórias que estavam espalhadas entre fila, lambda e state machine.
- `Testable Design and Quality Gates`: PASS. O quickstart e os contratos deixam claro o caminho real de validação ponta a ponta.
- `Simplicity, Observability, and Operational Reliability`: PASS. O fluxo direto reduz superfícies, mantém precisão dos filtros e preserva evidências operacionais úteis.

## Complexity Tracking

No constitution violations requiring justification.
