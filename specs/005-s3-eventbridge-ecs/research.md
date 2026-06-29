# Research: S3 EventBridge ECS

## Decision 1: Usar eventos diretos do Amazon S3 no EventBridge

**Decision**: O bucket de entrada publicará eventos de serviço do Amazon S3 diretamente no EventBridge, e a regra de dispatch filtrará `source = aws.s3` com `detail-type = Object Created`.

**Rationale**: A documentação oficial do EventBridge informa que o Amazon S3 envia eventos de serviço diretamente ao EventBridge, incluindo `Object Created`. Isso elimina a necessidade de SQS apenas para transportar notificações de criação de objeto até a camada de dispatch.

**Alternatives considered**:

- **S3 -> SQS**: descartado porque mantém uma camada intermediária cujo único papel é transportar o evento.
- **S3 -> Lambda -> EventBridge**: descartado porque adiciona código e operação sem necessidade funcional.
- **S3 via CloudTrail no EventBridge**: descartado porque o caso aqui é evento de serviço direto, mais simples e específico.

## Decision 2: A regra do EventBridge disparará `ecs:RunTask` diretamente

**Decision**: O target principal da regra EventBridge será a execução direta de uma task ECS sob demanda, usando `RoleARN` e parâmetros de ECS compatíveis com `RunTask`.

**Rationale**: A documentação oficial do EventBridge afirma que tarefas ECS podem ser usadas como targets e que, quando se usa `InputTransformer` para produzir um payload compatível com `TaskOverride`, os parâmetros são mapeados diretamente para `ecs.RunTask`. Isso permite passar o comando de processamento ao container sem Step Functions.

**Alternatives considered**:

- **EventBridge -> Step Functions -> ECS**: descartado porque adiciona uma camada de orquestração que não agrega valor ao objetivo de simplificação.
- **EventBridge -> Lambda -> ECS**: descartado porque reintroduz uma tradução de payload que o próprio EventBridge já pode fazer.
- **Serviço ECS com polling próprio**: descartado porque foge do modelo sob demanda desejado.

## Decision 3: O `processing_id` da tentativa será derivado do envelope do evento

**Decision**: O identificador da tentativa de processamento será derivado do identificador único do evento EventBridge, preservando o hash do PDF como identidade canônica do documento no worker.

**Rationale**: O evento `Object Created` do S3 no EventBridge traz um campo de topo `id` único por entrega. Esse identificador já existe no ponto de dispatch e evita depender de uma execução Step Functions para nomear a tentativa.

**Alternatives considered**:

- **Gerar `processing_id` dentro do script de teste**: descartado porque isso desloca para fora da infraestrutura uma responsabilidade do fluxo real.
- **Usar somente `bucket + object_key`**: descartado porque não diferencia reentregas ou reprocessamentos da mesma chave.
- **Usar o hash do PDF como `processing_id`**: descartado porque mistura identidade da tentativa com identidade canônica do documento.

## Decision 4: O pattern do EventBridge será preciso e evitará loops

**Decision**: A regra filtrará explicitamente o bucket de entrada e a chave elegível do objeto, usando operadores de comparação do EventBridge equivalentes a `incoming/*.pdf`, e o bucket de artefatos continuará separado do bucket de entrada.

**Rationale**: A documentação do EventBridge recomenda padrões precisos para evitar loops e matches indevidos, e também confirma suporte a operadores de comparação como `prefix`, `suffix` e `wildcard` em strings. Como o bucket de saída é separado, os artefatos produzidos não serão reprocessados por acidente.

**Alternatives considered**:

- **Pattern apenas com `source` e `detail-type`**: descartado porque é amplo demais e aumenta risco de disparos indevidos.
- **Mesmo bucket para entrada e artefatos sem filtros precisos**: descartado porque eleva o risco de loops e complica a operação.
- **Validação apenas dentro do worker**: descartado porque faria o ECS receber execuções evitáveis.

## Decision 5: O módulo Terraform será simplificado removendo os recursos intermediários

**Decision**: O módulo `faturama_runtime` deixará de declarar SQS, policy de queue, bucket notification para queue, Lambda de dispatch, archive file, Step Functions e roles associadas, mantendo S3, ECS, IAM e EventBridge como caminho principal.

**Rationale**: O estado atual do módulo mostra um encadeamento `S3 -> SQS -> Lambda -> EventBridge -> Step Functions -> ECS`. Como o novo contrato usa S3 direto no EventBridge e EventBridge direto no ECS, esses recursos passam a ser ruído operacional e devem sair do design.

**Alternatives considered**:

- **Manter os recursos antigos desativados por flag**: descartado porque preserva complexidade e drift desnecessários.
- **Criar um segundo módulo paralelo**: descartado porque duplicaria runtime e configuração sem necessidade.
- **Modificar somente scripts e manter a infraestrutura antiga**: descartado porque não resolve o requisito principal.

## Decision 6: A validação local continuará sendo totalmente provisionada por Terraform

**Decision**: O bootstrap local continuará subindo Docker Compose e aplicando Terraform contra o endpoint local, e o teste real seguirá fazendo apenas upload no S3 e observando o processamento assíncrono disparado pela infraestrutura.

**Rationale**: O usuário exigiu que a infraestrutura local fosse criada via Terraform e que o teste não invocasse o worker localmente. O ambiente local já possui cobertura para os recursos centrais do novo fluxo e pode continuar sendo a base da validação ponta a ponta.

**Alternatives considered**:

- **Criar recursos fora do Terraform com AWS CLI**: descartado porque viola a restrição explícita do projeto.
- **Invocar `run_processing_message` direto no script**: descartado porque não valida o fluxo real.
- **Trocar o teste por mocks ou adapters falsos**: descartado porque conflita com as decisões anteriores do projeto.

## Source References

- Amazon S3 events in EventBridge: `https://docs.aws.amazon.com/eventbridge/latest/ref/events-ref-s3.html`
- S3 EventBridge event structure: `https://docs.aws.amazon.com/AmazonS3/latest/userguide/ev-events.html`
- EventBridge targets and ECS tasks: `https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-targets.html`
- EventBridge input transformers: `https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-transform-input-rule.html`
- EventBridge pattern operators: `https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-pattern-operators.html`
- EventBridge pattern best practices: `https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-patterns-best-practices.html`
- Local resource coverage check used during planning: `AWS::S3::Bucket`, `AWS::Events::Rule`, `AWS::IAM::Role`, `AWS::ECS::Cluster`, `AWS::ECS::TaskDefinition` supported in MiniStack
