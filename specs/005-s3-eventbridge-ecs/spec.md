# Feature Specification: S3 EventBridge ECS

**Feature Branch**: `[005-s3-eventbridge-ecs]`

**Created**: 2026-06-28

**Status**: Draft

**Input**: User description: "$speckit-specify 1. S3 -> EventBridge -> ECS RunTask

  - É a opção mais simples para task sob demanda.
  - Remove SQS, Pipe e Step Functions.
  - Mantém só EventBridge.
  - Se o objetivo é simplicidade com ECS sob demanda, essa é a melhor arquitetura. redesenhar a infra para S3 -> EventBridge -> ECS via Terraform"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Disparar processamento direto por upload (Priority: P1)

Como operador da plataforma, quero que um arquivo enviado ao bucket de entrada dispare diretamente uma execução sob demanda do processador de faturas, para que o fluxo assíncrono real comece sem depender de camadas intermediárias de fila ou orquestração.

**Why this priority**: Esse é o objetivo central do redesenho. Sem o disparo direto a partir do evento do upload, a arquitetura continua mais complexa do que o necessário e não entrega a simplificação pedida.

**Independent Test**: Pode ser testada enviando um PDF elegível ao bucket de entrada e verificando que uma execução real do processador é iniciada a partir do evento de criação do objeto, sem intervenção manual e sem chamada local direta ao worker.

**Acceptance Scenarios**:

1. **Given** um bucket de entrada apto a receber PDFs elegíveis, **When** um novo arquivo é criado dentro do prefixo monitorado, **Then** o sistema inicia uma execução assíncrona real do processador para aquele arquivo.
2. **Given** um arquivo recém-enviado que atende aos critérios do fluxo, **When** o evento de criação é recebido, **Then** o processamento começa sem depender de fila intermediária, lambda de tradução ou máquina de estados.

---

### User Story 2 - Simplificar a operação da infraestrutura (Priority: P2)

Como responsável pela operação local e em nuvem, quero que a infraestrutura necessária para o processamento sob demanda seja mínima e provisionada integralmente por código, para que bootstrap, manutenção e diagnóstico fiquem previsíveis.

**Why this priority**: O problema atual não é apenas processar o arquivo, mas conseguir levantar e manter o fluxo com menos componentes, menos pontos de falha e menor custo operacional de entendimento.

**Independent Test**: Pode ser testada provisionando o ambiente do zero e confirmando que os recursos mínimos do fluxo são criados, o upload é aceito e o disparo real acontece sem necessidade de recursos intermediários desnecessários.

**Acceptance Scenarios**:

1. **Given** um ambiente local limpo, **When** a infraestrutura é provisionada, **Then** o fluxo de processamento assíncrono fica operacional usando somente os componentes necessários para disparo por evento e execução sob demanda.
2. **Given** a infraestrutura provisionada, **When** um operador revisa os recursos ativos do fluxo, **Then** ele encontra apenas armazenamento de entrada e saída, roteamento por evento e execução sob demanda do processador, sem camadas auxiliares desnecessárias.

---

### User Story 3 - Preservar rastreabilidade e resultado do processamento (Priority: P3)

Como consumidor do resultado, quero que a simplificação da arquitetura não elimine a rastreabilidade do upload nem a geração dos artefatos esperados, para que o fluxo continue útil e auditável.

**Why this priority**: Simplificar a arquitetura sem preservar o comportamento observável do processamento introduziria regressão funcional e tornaria a mudança operacionalmente arriscada.

**Independent Test**: Pode ser testada enviando um PDF conhecido e confirmando que os artefatos esperados são publicados no bucket de saída com correlação clara ao arquivo de entrada e à execução iniciada pelo evento.

**Acceptance Scenarios**:

1. **Given** um PDF processado com sucesso pelo fluxo direto por evento, **When** a execução termina, **Then** os artefatos esperados ficam disponíveis no bucket de saída com correlação clara ao processamento disparado.
2. **Given** um upload que falha durante o processamento, **When** o operador investiga a execução, **Then** ele consegue relacionar o arquivo enviado, a tentativa de processamento e a falha observada sem depender de componentes removidos do desenho anterior.

### Edge Cases

- O sistema deve ignorar arquivos criados fora do prefixo de entrada definido para processamento.
- O sistema deve evitar reações indevidas a artefatos gravados no bucket de saída para não criar loops de processamento.
- O sistema deve lidar com eventos duplicados de criação do mesmo objeto sem gerar multiplicação indevida de resultados canônicos.
- O sistema deve tratar uploads incompletos, corrompidos ou incompatíveis sem bloquear o processamento de outros arquivos.
- O sistema deve continuar rastreável mesmo quando a execução sob demanda falha antes de publicar qualquer artefato de saída.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST iniciar o processamento assíncrono real a partir da criação de um objeto elegível no bucket de entrada.
- **FR-002**: O sistema MUST acionar diretamente a execução sob demanda do processador a partir do evento do armazenamento, sem depender de fila intermediária, função tradutora ou orquestrador adicional no caminho principal.
- **FR-003**: O sistema MUST limitar o disparo automático ao prefixo de entrada definido para documentos elegíveis.
- **FR-004**: O sistema MUST impedir que gravações no bucket de saída acionem novo processamento automático.
- **FR-005**: O sistema MUST manter o fluxo integralmente provisionável por infraestrutura como código, incluindo os recursos necessários para entrada, roteamento do evento e execução do processador.
- **FR-006**: O sistema MUST permitir bootstrap local reprodutível do fluxo completo com os mesmos contratos operacionais usados pela aplicação.
- **FR-007**: O sistema MUST iniciar uma execução independente para cada upload elegível aceito, sem exigir chamada manual ao worker a partir de scripts de teste.
- **FR-008**: O sistema MUST preservar a capacidade do worker de ler o arquivo enviado diretamente do armazenamento configurado e publicar os artefatos resultantes no bucket de saída.
- **FR-009**: O sistema MUST preservar correlação auditável entre arquivo de entrada, tentativa de processamento e artefatos produzidos.
- **FR-010**: O sistema MUST expor evidências operacionais suficientes para confirmar se um upload gerou ou não uma execução real do processador.
- **FR-011**: O sistema MUST permitir que um teste ponta a ponta valide o caminho real desde o upload do PDF até a observação dos artefatos de saída, sem invocar o código de processamento localmente.
- **FR-012**: O sistema MUST manter isolamento de falha entre execuções para que um documento problemático não impeça o disparo e o processamento dos demais.
- **FR-013**: O sistema MUST continuar suportando idempotência e rastreabilidade já exigidas pelo processamento de faturas, mesmo com a simplificação do caminho de disparo.

### Key Entities *(include if feature involves data)*

- **Arquivo de Entrada**: Documento enviado ao bucket monitorado e elegível para iniciar o processamento.
- **Evento de Criação de Objeto**: Registro da criação do arquivo de entrada que dispara a execução sob demanda.
- **Execução de Processamento**: Tentativa assíncrona iniciada a partir do evento do arquivo, responsável por buscar o PDF, processá-lo e publicar resultados.
- **Artefato de Saída**: Arquivo derivado do processamento publicado no bucket de saída e correlacionado à execução correspondente.
- **Evidência Operacional**: Conjunto mínimo de sinais observáveis usado para provar que o upload acionou uma execução real e para diagnosticar falhas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos uploads elegíveis usados no teste ponta a ponta iniciam uma execução real do processador sem invocação manual local.
- **SC-002**: 100% dos ambientes locais provisionados do zero conseguem ativar o fluxo completo de upload para execução sob demanda usando apenas o bootstrap documentado.
- **SC-003**: Pelo menos 95% dos PDFs válidos enviados em condições normais geram artefatos observáveis no bucket de saída em até 5 minutos após o upload.
- **SC-004**: 100% das execuções iniciadas a partir do upload possuem evidência operacional suficiente para confirmar disparo, sucesso ou falha.
- **SC-005**: O número de componentes obrigatórios no caminho principal do disparo assíncrono é reduzido em relação ao desenho anterior, sem perda do processamento real ponta a ponta.

## Assumptions

- O processamento funcional do PDF continua sendo responsabilidade do worker já existente e não será redefinido por esta feature.
- A simplificação desejada se concentra no caminho de disparo assíncrono da infraestrutura, e não na lógica de extração de dados da fatura.
- O bucket de entrada e o bucket de saída continuarão separados para evitar loops e preservar rastreabilidade.
- O teste de validação da feature deve usar upload real no armazenamento emulado/compatível e observar o comportamento real da infraestrutura provisionada.
- O bootstrap local continuará sendo a forma oficial de subir o ambiente completo para validação.
- A solução precisa funcionar sem chamadas locais diretas ao código de processamento como atalho de teste ou fallback operacional.
