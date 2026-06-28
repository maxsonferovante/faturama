# Implementation Plan: Processamento Assincrono de Faturas por Eventos

**Branch**: `[main]` | **Date**: 2026-06-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-event-driven-file-processing/spec.md`

## Summary

Encapsular o pipeline CLI atual em um worker container acionado por `URL assinada -> S3 -> SQS -> EventBridge Pipe -> Step Functions -> ECS`, salvando os artefatos OpenDataLoader em `processados-faturama`, migrando a persistência durável do fluxo assíncrono para PostgreSQL e estabelecendo um read model de status consultado por outra API, tudo provisionado por Terraform com validação local via Docker e emulador AWS compatível.

## Technical Context

**Language/Version**: Python 3.12+ para a aplicação; Terraform HCL para infraestrutura; Docker Compose para desenvolvimento local

**Primary Dependencies**: `langgraph`, `langgraph-checkpoint-sqlite` como referência de workflow existente, `opendataloader-pdf[hybrid]`, `langchain-opendataloader-pdf`, `pydantic`, AWS SDK para Python para S3 e geração/validação de uploads assinados, driver PostgreSQL, Terraform AWS provider

**Storage**: Amazon S3 para PDFs de entrada em `pre-processamento-faturama` e artefatos OpenDataLoader/resultados derivados em `processados-faturama`; PostgreSQL em RDS para ledger de status, checkpoints, revisão, vínculo do upload autorizado, manifesto dos artefatos e dados canônicos; PostgreSQL local compatível em Docker para desenvolvimento

**Testing**: `pytest` para unidade, contrato, integração e e2e; `terraform validate`; cenários ponta a ponta locais com Docker, Terraform e upload real de PDF no ambiente emulado

**Target Platform**: ECS task sob demanda em ambiente AWS; ambiente local em Docker com emulação AWS compatível e PostgreSQL local

**Project Type**: backend Python orientado a workflow com worker assíncrono e infraestrutura como código

**Performance Goals**: aceitar uploads sem bloqueio síncrono por URL assinada; iniciar o dispatch assíncrono em até 30 segundos após o evento chegar à fila; concluir uma fatura suportada em até 5 minutos desde o upload; propagar mudanças de estado para a API de status baseada em banco em até 30 segundos; manter consultas persistidas em até 5 segundos; sustentar um burst de 20 uploads concorrentes elegíveis na v1

**Constraints**: desenvolvimento ordinário sem AWS real; Step Function deve disparar ECS sem aguardar conclusão; `processing_id` identifica tentativa e o hash do PDF identifica o documento canônico; `REVIEW_REQUIRED` deve permanecer não terminal; artefatos OpenDataLoader devem ir para `processados-faturama` com chave rastreável persistida no banco; menor privilégio IAM; evitar loops de notificação no bucket; documentar diferenças inevitáveis entre ambiente local e AWS real; a leitura de status será feita por outra API apoiada no banco, não pelo worker; os eventos de ciclo de vida da v1 são persistidos internamente no ledger/read model e não exigem publisher externo obrigatório

**Scale/Scope**: v1 cobre um bucket de entrada, uma fila principal, um pipe, uma state machine, um cluster ECS e um banco PostgreSQL compartilhado para dezenas a centenas de PDFs por dia, com alvo mínimo validado de burst de 20 uploads concorrentes e vazão diária de 100 PDFs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Pythonic Correctness and Readability`: PASS. O desenho preserva um worker Python explícito, contratos tipados e reaproveita o runtime existente sem ocultar novas integrações em scripts opacos.
- `Clean Architecture Boundaries`: PASS. S3, SQS, Step Functions, ECS, PostgreSQL e Terraform ficam confinados a adapters de infraestrutura, enquanto a política de processamento continua na aplicação e no domínio.
- `Object-Oriented Design and SOLID`: PASS. O plano separa ingestão de eventos, normalização de payload, execução do worker, persistência operacional e persistência canônica em responsabilidades distintas.
- `Testable Design and Quality Gates`: PASS. A feature exige testes por camada, validação Terraform e fluxo e2e local com upload real para provar o caminho assíncrono.
- `Simplicity, Observability, and Operational Reliability`: PASS. O fluxo usa serviços gerenciados simples, contratos claros, retries explícitos, status persistido e trilha observável por execução.

## Project Structure

### Documentation (this feature)

```text
specs/004-event-driven-file-processing/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── orchestration.md
│   ├── processing-message.md
│   ├── signed-upload.md
│   ├── status-read-model.md
│   └── runtime-config.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── faturama/
    ├── application/
    │   ├── dto/
    │   ├── ports/
    │   ├── services/
    │   └── use_cases/
    ├── domain/
    │   ├── entities/
    │   ├── services/
    │   ├── value_objects/
    │   └── exceptions.py
    ├── infrastructure/
    │   ├── aws/
    │   ├── config/
    │   ├── database/
    │   ├── messaging/
    │   ├── opendataloader/
    │   └── repositories/
    ├── interface/
    │   ├── cli/
    │   └── worker/
    ├── observability/
    └── shared/

infra/
└── terraform/
    ├── modules/
    │   └── faturama_runtime/
    └── environments/
        ├── local/
        └── aws/

docker/
└── worker/

tests/
├── contract/
├── e2e/
├── integration/
└── unit/
```

**Structure Decision**: Manter a base Python em `src/` e adicionar um entrypoint de worker em `src/faturama/interface/worker` que consome o contrato assíncrono e delega ao pipeline existente. Terraform e bootstrap local ficam fora do pacote Python em `infra/terraform` e `docker/worker`, preservando o limite entre código de aplicação e infraestrutura. Os contratos de URL assinada e do read model de status ficam documentados nesta feature porque a API emissora e a API leitora pertencem ao contexto maior, não ao worker em si.

## Phase 0: Research Summary

As decisões de pesquisa foram consolidadas em [research.md](./research.md) com foco em: usar URL assinada como mecanismo de entrada externa, usar EventBridge Pipe para ligar SQS à Step Function sem componente extra, usar Step Functions Standard com integração `ecs:runTask` sem espera, distinguir `processing_id` de tentativa e hash do PDF como identidade canônica, persistir artefatos OpenDataLoader em `processados-faturama` com manifesto auditável no banco, manter `REVIEW_REQUIRED` como estado pendente não terminal, expor status por outra API apoiada no banco e documentar a paridade local com emulação AWS mais PostgreSQL compatível.

## Phase 1: Design Summary

- O modelo de dados operacional e sua relação com os dados canônicos existentes foram definidos em [data-model.md](./data-model.md).
- Os contratos externos do fluxo assíncrono foram definidos em [contracts/processing-message.md](./contracts/processing-message.md), [contracts/orchestration.md](./contracts/orchestration.md), [contracts/signed-upload.md](./contracts/signed-upload.md), [contracts/status-read-model.md](./contracts/status-read-model.md) e [contracts/runtime-config.md](./contracts/runtime-config.md).
- O guia de validação local e ponta a ponta foi documentado em [quickstart.md](./quickstart.md), cobrindo provisionamento Terraform, upload por URL assinada, dispatch assíncrono, persistência dos artefatos OpenDataLoader em bucket dedicado, polling de status, observabilidade, idempotência, ordering/deduplicação de eventos e metas temporais/concorrentes da v1.
- O bloco gerenciado do agente deve apontar para este plano após a atualização de contexto.

## Post-Design Constitution Check

- `Pythonic Correctness and Readability`: PASS. Os artefatos mantêm contratos pequenos e nomenclatura alinhada ao runtime atual.
- `Clean Architecture Boundaries`: PASS. O desenho introduz ports claros para armazenamento de objetos, persistência PostgreSQL e consumo de mensagens sem vazar SDKs para domínio ou aplicação de alto nível.
- `Object-Oriented Design and SOLID`: PASS. Cada novo componente proposto tem responsabilidade única: intake, normalização, execução, persistência, observabilidade ou provisão de infraestrutura.
- `Testable Design and Quality Gates`: PASS. O plano define validação local reprodutível e cobertura de testes por interface, integração e fluxo completo.
- `Simplicity, Observability, and Operational Reliability`: PASS. O fluxo evita Lambdas auxiliares desnecessárias, privilegia contratos simples, registra estados terminais e explicita as diferenças de paridade local.

## Complexity Tracking

No constitution violations requiring justification.
