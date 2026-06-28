# Feature Specification: Processamento Assincrono de Faturas por Eventos

**Feature Branch**: `[004-event-driven-file-processing]`

**Created**: 2026-06-28

**Status**: Draft

**Input**: User description: "$speckit-specify Dada que a pipeline esta funcional via CLI, vamos disponibilizar o acesso a pipelie em uma infraestrutura mais robusta e escalavel, aderente a uma arquitetura de nuvem. Para que funcione como um processador de arquivos de forma assincrono dentro de uma arquiteutra orientada a eventos, em um contexto maior."

## Clarifications

### Session 2026-06-28

- Q: Qual deve ser a regra principal de idempotência? → A: hash do PDF + `processing_id` por tentativa
- Q: Quem pode iniciar o processamento? → A: upload externo via URL assinada
- Q: Como o sistema consumidor descobre a conclusão? → A: apenas consulta de status
- Q: Como tratar uma solicitação que entra em revisão? → A: `REVIEW_REQUIRED` pendente não terminal
- Q: Quem pode consultar o status de uma solicitação? → A: outra API via banco
- Q: Onde os arquivos gerados pelo OpenDataLoader serão salvos? → A: bucket `processados-faturama` com chave rastreável persistida no banco

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submeter arquivos sem bloqueio (Priority: P1)

Como sistema integrador, quero enviar arquivos de fatura para processamento assíncrono por um mecanismo de upload externo autorizado e receber um acompanhamento rastreável da solicitação para que a pipeline possa participar de um contexto maior sem depender de execução manual e síncrona.

**Why this priority**: Sem uma entrada assíncrona e rastreável, a pipeline continua limitada ao uso operacional local e não consegue atuar como componente de uma arquitetura mais robusta e escalável.

**Independent Test**: Pode ser testada enviando um arquivo suportado para o fluxo assíncrono e confirmando que a solicitação é aceita, ganha identificação própria, evolui de estado e produz resultado sem bloquear o solicitante.

**Acceptance Scenarios**:

1. **Given** um arquivo de fatura suportado ainda não processado, **When** um sistema externo o submete para processamento, **Then** a solicitação é aceita de forma assíncrona, recebe um identificador rastreável e entra em uma fila de execução sem exigir espera pelo resultado final.
2. **Given** uma solicitação já aceita, **When** o processamento avança até a conclusão, **Then** o solicitante consegue consultar o estado atual e obter referência clara para o resultado estruturado produzido.

---

### User Story 2 - Operar o fluxo por eventos com revisão controlada (Priority: P2)

Como operador do processo, quero que cada mudança relevante do ciclo de processamento gere um evento de ciclo de vida persistido no ledger operacional e projetado no read model de status, preservando a revisão assistida quando houver ambiguidade, para que o fluxo continue governável mesmo em escala maior.

**Why this priority**: Escalabilidade sem visibilidade operacional e sem tratamento de pendências cria filas opacas, dificulta diagnóstico e compromete a confiabilidade do processo.

**Independent Test**: Pode ser testada processando um arquivo com ambiguidade e verificando que o ciclo de vida da solicitação é persistido e projetado no read model, pausa quando necessário para revisão e retoma sem perder o histórico da execução.

**Acceptance Scenarios**:

1. **Given** uma solicitação em processamento, **When** ela muda de etapa relevante, **Then** o sistema registra um evento de ciclo de vida persistido e projeta a transição de estado de forma consultável para que operadores e sistemas consumidores acompanhem o ciclo de vida sem depender de interpretação informal.
2. **Given** uma solicitação com itens ambíguos, **When** o processamento alcança o ponto de decisão, **Then** o sistema mantém a pendência de revisão no mesmo ciclo de vida da solicitação e permite retomada posterior sem reiniciar todo o fluxo.

---

### User Story 3 - Consumir resultados sem regressao funcional (Priority: P3)

Como consumidor dos dados estruturados, quero receber os mesmos resultados funcionais da pipeline atual dentro do novo fluxo assíncrono para que a evolução de infraestrutura não reduza a utilidade prática já entregue pela solução.

**Why this priority**: A mudança de arquitetura só gera valor se preservar a consistência do resultado de negócio e a segurança contra duplicações, perdas e consultas inconsistentes.

**Independent Test**: Pode ser testada processando documentos conhecidos pelo novo fluxo e verificando que os dados estruturados, as consultas esperadas e a separação entre fatos observados e projeções continuam corretos mesmo com reenvio e concorrência.

**Acceptance Scenarios**:

1. **Given** uma fatura processada com sucesso pelo novo fluxo, **When** um consumidor acessa o resultado disponibilizado, **Then** encontra os mesmos dados estruturados essenciais já esperados pela solução, com rastreabilidade e separação entre valores observados e projetados.
2. **Given** um mesmo arquivo submetido novamente por engano ou por retentativa operacional, **When** o sistema trata a nova solicitação, **Then** ele evita duplicação indevida de resultados canônicos e mantém histórico claro do reprocessamento.

### Edge Cases

- O mesmo conteúdo de PDF pode ser submetido várias vezes com chaves ou tentativas diferentes, mas o sistema deve reconhecer a identidade canônica pelo hash do arquivo e tratar cada `processing_id` apenas como uma tentativa operacional separada.
- Como o sistema se comporta quando um arquivo aceito para processamento se torna ilegível, incompleto ou incompatível antes da conclusão?
- Como o sistema trata eventos fora de ordem, repetidos ou atrasados sem corromper o estado da solicitação?
- Como o fluxo lida com solicitações que ficam aguardando revisão por longos períodos sem bloquear o processamento das demais?
- Como o sistema evita que a falha de uma solicitação impeça o avanço de outras solicitações independentes?
- Como o sistema reage quando o processamento conclui, mas a gravação dos artefatos do OpenDataLoader no bucket `processados-faturama` falha ou fica incompleta?
- Como o resultado final é preservado quando uma solicitação conclui com avisos ou com processamento parcialmente aproveitável?
- Como o sistema mantém consistência quando um consumidor tenta usar o resultado antes de a solicitação alcançar um estado terminal apropriado?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST aceitar solicitações assíncronas de processamento de arquivos de fatura vindas de um contexto externo ao uso manual local.
- **FR-001a**: O sistema MUST permitir, na v1, que sistemas externos autorizados iniciem o processamento por meio de URLs de upload assinadas e temporárias, sem exigir credenciais permanentes de infraestrutura para cada remetente.
- **FR-002**: O sistema MUST registrar cada solicitação aceita como uma unidade rastreável com identificador próprio, origem, horário de recebimento e estado atual.
- **FR-003**: O sistema MUST conduzir cada solicitação por um ciclo de vida explícito, incluindo no mínimo estados de recebida, em espera, em processamento, aguardando revisão quando aplicável, concluída e falha.
- **FR-003a**: O sistema MUST tratar `REVIEW_REQUIRED` como estado pendente não terminal, permitindo retomada posterior sem encerrar a solicitação como sucesso parcial ou falha definitiva.
- **FR-004**: O sistema MUST permitir que o solicitante acompanhe o estado e o histórico resumido de cada solicitação por um read model persistido, sem depender de acesso direto ao ambiente operacional interno.
- **FR-004a**: O sistema MUST adotar a consulta de status como canal oficial de descoberta de conclusão, revisão necessária, falha ou parcialidade para sistemas consumidores na v1.
- **FR-004b**: O sistema MUST disponibilizar o read model de status para consumo por outra API apoiada no banco de dados persistido, em vez de expor a consulta diretamente pelo componente de ingestão assíncrona.
- **FR-005**: O sistema MUST processar cada arquivo aceito sem bloquear a confirmação inicial de recebimento da solicitação.
- **FR-006**: O sistema MUST preservar no fluxo assíncrono a mesma finalidade funcional já validada na pipeline atual, incluindo extração de dados estruturados, rastreabilidade, persistência canônica e capacidade de consulta posterior.
- **FR-006a**: O sistema MUST salvar os arquivos gerados pelo OpenDataLoader em um bucket dedicado chamado `processados-faturama`.
- **FR-006b**: O sistema MUST atribuir a cada artefato salvo no bucket `processados-faturama` uma chave rastreável e determinística o suficiente para correlacionar o artefato à solicitação, ao documento canônico e à tentativa de processamento.
- **FR-006c**: O sistema MUST persistir no banco de dados a referência aos artefatos salvos em `processados-faturama`, incluindo ao menos bucket, chave rastreável, tipo de artefato e vínculo com a solicitação, para fins de auditoria, avaliação e consulta posterior.
- **FR-007**: O sistema MUST registrar eventos de ciclo de vida persistidos para transições relevantes da solicitação, incluindo aceitação, início de processamento, necessidade de revisão, conclusão e falha, preservando-os para consulta auditável e projeção do read model.
- **FR-008**: O sistema MUST disponibilizar o resultado estruturado final ou parcial com uma referência inequívoca à solicitação que o originou.
- **FR-009**: O sistema MUST manter idempotência para submissões repetidas do mesmo documento reconhecendo a identidade canônica pelo hash do conteúdo do PDF, mesmo quando houver nova chave de objeto ou nova tentativa operacional.
- **FR-009a**: O sistema MUST tratar `processing_id` como identificador da tentativa de processamento e não como chave canônica do documento.
- **FR-010**: O sistema MUST isolar falhas por solicitação, de modo que o insucesso de um arquivo não interrompa o processamento das demais solicitações independentes.
- **FR-011**: O sistema MUST registrar motivo de falha, motivo de bloqueio e contexto operacional suficiente para diagnóstico quando uma solicitação não alcançar conclusão normal.
- **FR-012**: O sistema MUST preservar o tratamento de ambiguidades dentro do fluxo assíncrono, permitindo revisão manual e retomada controlada sem perder histórico da solicitação.
- **FR-013**: O sistema MUST distinguir, em toda saída disponibilizada ao contexto maior, entre resultado definitivo, resultado parcial, pendência de revisão e falha terminal.
- **FR-013a**: O sistema MUST expor `REVIEW_REQUIRED` como estado consultável distinto de `SUCCESS`, `PARTIAL` e `FAILED`.
- **FR-014**: O sistema MUST manter separados os valores observados em documentos processados e os valores projetados para competências futuras em todo resultado exposto.
- **FR-015**: O sistema MUST permitir reprocessamento seguro de solicitações falhas ou incompletas sem duplicar dados já aceitos de forma canônica.
- **FR-016**: O sistema MUST suportar, na v1, pelo menos um burst de 20 uploads concorrentes e uma vazão diária de 100 PDFs sem exigir coordenação humana caso a caso para arquivos suportados que não apresentem ambiguidade.
- **FR-017**: O sistema MUST preservar trilha auditável da solicitação desde o recebimento do arquivo até o estado terminal, incluindo decisões relevantes, pendências e resultado produzido.
- **FR-018**: O sistema MUST disponibilizar no read model um estado confiável, com sinalização de terminalidade e timestamp da última transição, para que sistemas consumidores saibam quando podem reagir ao resultado de uma solicitação sem depender de interpretação informal.
- **FR-019**: O sistema MUST vincular cada upload externo aceito à autorização temporária que o originou, preservando rastreabilidade suficiente para auditoria e investigação operacional.

### Key Entities *(include if feature involves data)*

- **Solicitacao de Processamento**: Representa o pedido assíncrono para tratar um arquivo de fatura, com identificador da tentativa, origem, estado atual e histórico resumido.
- **Arquivo Submetido**: Representa o documento recebido para processamento, com vínculo à solicitação, atributos de origem e evidências necessárias para auditoria.
- **Evento de Ciclo de Vida**: Representa um registro persistido de uma mudança relevante de estado da solicitação, usado para auditoria e para projeção do read model consumido por outros componentes do contexto maior.
- **Resultado Estruturado da Fatura**: Representa o conjunto de dados financeiros e metadados produzidos pela pipeline e disponibilizados para consultas e integrações posteriores.
- **Artefato Processado OpenDataLoader**: Representa cada arquivo derivado do processamento documental salvo no bucket `processados-faturama`, com chave rastreável e referência persistida no banco.
- **Pendencia de Revisao**: Representa uma interrupção controlada causada por ambiguidade, inconsistência ou insuficiência de evidência para aceitação automática segura.
- **Historico Operacional da Solicitacao**: Representa a sequência auditável de decisões, transições e ocorrências relevantes do processamento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das solicitações aceitas recebem identificador rastreável e estado inicial observável no momento do recebimento.
- **SC-001a**: 100% dos uploads aceitos por remetentes externos expiram automaticamente fora da janela autorizada e permanecem vinculados ao contexto do solicitante que os originou.
- **SC-002**: Pelo menos 95% dos arquivos suportados submetidos em condições normais alcançam um estado terminal apropriado com resultado disponível em até 5 minutos após a aceitação.
- **SC-002a**: 100% das execuções que produzirem artefatos do OpenDataLoader persistem referências consultáveis desses artefatos no banco e no bucket `processados-faturama` antes de serem consideradas concluídas com sucesso.
- **SC-003**: Em um conjunto de validação com reenvios intencionais do mesmo documento, a taxa de duplicação indevida de registros canônicos permanece em 0%.
- **SC-004**: 100% das transições para conclusão, revisão necessária ou falha ficam disponíveis ao contexto maior em até 30 segundos após ocorrerem.
- **SC-004a**: 100% das solicitações em estado terminal ficam visíveis na consulta oficial de status em até 30 segundos após a transição final.
- **SC-004b**: 100% das solicitações que entrarem em revisão ficam visíveis como `REVIEW_REQUIRED` na consulta oficial de status em até 30 segundos após a pausa operacional.
- **SC-004c**: 100% das solicitações aceitas ficam disponíveis para leitura pela API de status baseada em banco em até 30 segundos após cada transição relevante de estado.
- **SC-005**: Em pelo menos 95% das solicitações que param por falha ou revisão, um operador consegue identificar a causa principal em menos de 3 minutos apenas pela trilha operacional registrada.
- **SC-006**: 100% dos resultados disponibilizados para consumo externo preservam a separação entre fatos observados, projeções futuras e estados não conclusivos.
- **SC-007**: Em um burst de 20 solicitações concorrentes elegíveis, pelo menos 90% são concluídas sem intervenção humana adicional além da revisão já prevista para casos ambíguos.

## Assumptions

- A pipeline atual via CLI já representa o comportamento funcional de referência para processamento de faturas e deve ser preservada em seus resultados essenciais.
- A nova feature amplia a forma de acesso e operação da pipeline, sem redefinir o modelo canônico de dados financeiros já estabelecido pelo produto.
- Cada solicitação de processamento informa o contexto mínimo necessário para identificar sua origem e correlacionar seu resultado com o sistema solicitante.
- O canal externo inicial da v1 será baseado em autorização temporária de upload, e não em credenciais permanentes distribuídas para cada integrador.
- A identidade canônica de um documento no fluxo assíncrono continuará sendo determinada pelo hash do PDF, enquanto cada `processing_id` representará apenas uma tentativa operacional rastreável.
- Os artefatos gerados pelo OpenDataLoader precisam permanecer disponíveis no bucket `processados-faturama` com referência persistida no banco para auditoria, avaliação e consulta posterior.
- A v1 não exige publisher externo de evento de conclusão para consumidores; o mecanismo oficial de acompanhamento e reação será a consulta de status da solicitação.
- Solicitações em revisão permanecem abertas até retomada ou resolução explícita, usando `REVIEW_REQUIRED` como estado pendente oficial.
- A consulta de status da v1 será servida por outra API apoiada no banco de dados do processamento, e não pelo worker ou pelo fluxo de ingestão em si.
- Os eventos de ciclo de vida da v1 são persistidos internamente para auditoria e projeção do read model, podendo servir a publishers futuros sem alterar o contrato atual.
- O alvo mínimo de validação concorrente da v1 é um burst de 20 uploads elegíveis e uma vazão diária de 100 PDFs.
- O escopo desta feature cobre processamento assíncrono de arquivos de fatura e sua integração orientada a eventos, não a construção de interfaces visuais dedicadas.
- Casos ambíguos continuam sujeitos ao mesmo princípio de revisão controlada já adotado pela solução, ainda que o restante do fluxo opere sem bloqueio síncrono.
- O contexto maior que consumirá os resultados sabe tratar estados intermediários e terminais sem assumir que toda solicitação aceita será concluída com sucesso pleno.
- A primeira versão em nuvem prioriza robustez operacional, rastreabilidade e escalabilidade do processamento antes de otimizações adicionais de experiência para consumo humano direto.
