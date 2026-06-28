# Feature Specification: Alinhamento de Runtime da Arquitetura

**Feature Branch**: `[003-align-runtime-architecture]`

**Created**: 2026-06-27

**Status**: Draft

**Input**: User description: "$speckit-specify eu fiz duas interacoes /Users/mferovante/Documents/faturama/specs/001-invoice-extractor /Users/mferovante/Documents/faturama/specs/002-usage-report para implementacao de uma Construir um pipeline para transformar faturas de cartão em dados estruturados, consultáveis por mês, cartão, compra, parcela e saldo futuro, com separação clara entre extração, interpretação assistida e persistência, que usasse LangGraph e OpenDataLoader, mas nao foi feito LangGraph e OpenDataLoader como declarados sem integração real de runtime,. Eu quero corrigir isso e passar a usar VERDADEIRAMENTE ESSAS DUAS LIBS PYTHON CADA UMA PARA OS SEUS DEVIDOS PROPOSSITOS DENTRO DO PROJETO COMO CITADO NAS SPECS.MD"

## Clarifications

### Session 2026-06-27

- Q: Como o sistema deve reagir quando a extração primária falhar? → A: Encerrar como erro/partial explícito e remover fallback legado.
- Q: Qual deve ser a autoridade do agente de IA na revisão? → A: O agente pode decidir e aplicar automaticamente casos ambíguos elegíveis.
- Q: Qual deve ser o critério de elegibilidade para autoaplicação do agente? → A: Autoaplicar apenas casos com limiar alto específico de confiança.
- Q: Como tratar falhas após o início do workflow quanto à persistência? → A: Persistir tudo que for possível em qualquer ponto, mesmo com contexto incompleto.
- Q: Como tratar o histórico legado já persistido pelo runtime antigo? → A: Invalidar histórico legado e exigir reconstrução manual antes de qualquer consulta.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Executar o pipeline prometido em runtime (Priority: P1)

Como mantenedor do pipeline, quero que a ingestão de uma fatura execute em runtime os mesmos componentes centrais já aprovados na arquitetura para que o comportamento real do produto finalmente corresponda ao que foi especificado.

**Why this priority**: Enquanto o fluxo principal continuar apoiado em atalhos paralelos ou artefatos pré-gerados, a entrega principal do produto permanece desalinhada com a arquitetura prometida e com a confiança esperada pelos mantenedores.

**Independent Test**: Pode ser testada processando uma fatura suportada do início ao fim e verificando que a extração primária, a coordenação do fluxo e a persistência auditável ocorrem dentro do pipeline oficial, sem depender de um caminho substituto externo ao runtime principal.

**Acceptance Scenarios**:

1. **Given** uma fatura suportada ainda não processada, **When** o usuário executa a ingestão oficial do produto, **Then** o pipeline usa os componentes arquiteturais prometidos para extrair o documento, coordenar o fluxo e persistir o resultado estruturado auditável.
2. **Given** uma execução concluída com sucesso, **When** o mantenedor inspeciona as evidências operacionais geradas pelo processamento, **Then** ele consegue confirmar que o resultado veio do fluxo principal prometido e não de um atalho paralelo sem integração real.

---

### User Story 2 - Preservar interpretação assistida e revisão sem rotas paralelas (Priority: P2)

Como operador do processo, quero que ambiguidades e decisões de confiança continuem tratadas de forma assistida dentro do mesmo fluxo principal, com aplicação automática quando o caso for elegível, para que a revisão operacional permaneça consistente mesmo após a correção da aderência de runtime.

**Why this priority**: Corrigir a aderência tecnológica sem preservar a governança de confiança, revisão e retomada quebraria o valor operacional da v1.

**Independent Test**: Pode ser testada processando uma fatura com itens ambíguos e confirmando que a triagem, a decisão automática elegível ou a revisão humana necessária e a retomada acontecem sem desviar para uma implementação paralela.

**Acceptance Scenarios**:

1. **Given** uma fatura com trechos ambíguos elegíveis para decisão automática, **When** o pipeline alcança esse ponto do fluxo, **Then** o agente de IA pode decidir e aplicar a resolução dentro do mesmo workflow, preservando rastreabilidade completa.
2. **Given** uma pendência que ainda exija intervenção humana, **When** o operador revisa e o processamento é retomado, **Then** o sistema continua do ponto apropriado sem reiniciar por um caminho alternativo nem perder rastreabilidade das decisões anteriores.

---

### User Story 3 - Reprocessar e consultar sem regressão funcional (Priority: P3)

Como usuário da base consolidada, quero continuar consultando gastos, parcelas e saldo futuro após a correção do runtime para que a troca do caminho interno de execução não reduza a utilidade prática já prometida pela solução.

**Why this priority**: A correção só é válida se preservar o resultado funcional esperado do produto para consultas e reprocessamento seguro.

**Independent Test**: Pode ser testada reprocessando um mesmo documento já conhecido e consultando seus dados estruturados para verificar continuidade funcional, idempotência e consistência entre observado e projetado.

**Acceptance Scenarios**:

1. **Given** um documento já processado anteriormente, **When** o usuário solicita novo processamento pelo fluxo oficial corrigido, **Then** o sistema atualiza ou reconfirma o resultado sem duplicar registros nem degradar a consistência histórica.
2. **Given** faturas já persistidas após a correção, **When** o usuário consulta mês, cartão, compra, parcela ou saldo futuro, **Then** as respostas permanecem disponíveis com separação clara entre fatos observados e projeções futuras.

### Edge Cases

- Quando o componente primário de extração não conseguir produzir conteúdo suficiente para continuar o fluxo principal, o sistema deve encerrar a execução como erro ou resultado parcial explícito, sem fallback para sidecars legados.
- Como o sistema deve se comportar quando a execução é interrompida entre etapas auditáveis e precisa ser retomada sem perder contexto?
- Como o sistema trata diferenças materiais entre o resultado do fluxo oficial corrigido e resultados antigos gerados por caminhos substitutos?
- Resultados históricos produzidos pelo runtime legado devem ser invalidados e ficar indisponíveis para consulta até reconstrução manual sob o novo fluxo oficial.
- Em falhas ocorridas após o início do workflow, o sistema deve persistir tudo que for possível com contexto operacional explícito, mesmo quando o resultado final permanecer incompleto.
- Como o sistema evita regressão operacional quando apenas parte da fatura pode ser tratada automaticamente e o restante exige revisão humana?
- Como o sistema lida com documentos suportados por regras de negócio existentes, mas ainda não suficientemente cobertos pelo fluxo principal corrigido?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST executar o processamento oficial de faturas usando, em runtime, os mesmos componentes centrais já aprovados pela arquitetura para extração documental primária e coordenação do workflow principal.
- **FR-002**: O sistema MUST eliminar a dependência do fluxo principal em caminhos substitutos que apenas simulam a arquitetura prometida sem integração real no runtime oficial.
- **FR-002a**: O sistema MUST encerrar a execução com erro ou resultado parcial explícito quando a extração primária não conseguir produzir artefatos suficientes, sem recorrer a fallback legado baseado em sidecars externos ao runtime oficial.
- **FR-003**: O sistema MUST manter separação explícita entre extração documental, interpretação assistida, revisão operacional e persistência canônica, mesmo quando essas etapas participarem do mesmo fluxo coordenado.
- **FR-004**: O sistema MUST produzir evidências operacionais suficientes para demonstrar qual etapa do fluxo oficial executou cada transformação relevante do documento até a persistência final.
- **FR-005**: O sistema MUST continuar registrando metadados essenciais da fatura, lançamentos relevantes, vínculos parcelados, projeções futuras e justificativas de decisão no mesmo histórico auditável já prometido ao usuário.
- **FR-006**: O sistema MUST preservar o tratamento de confiança e ambiguidade dentro do fluxo principal corrigido, incluindo aplicação automática por agente de IA em casos elegíveis, fila de revisão para casos não elegíveis e retomada controlada.
- **FR-006a**: O sistema MUST registrar, para cada decisão automática aplicada pelo agente de IA, a justificativa operacional, a evidência usada e a origem da decisão de forma auditável.
- **FR-006b**: O sistema MUST permitir autoaplicação pelo agente de IA apenas quando o caso atingir um limiar alto específico de confiança, distinto e mais restritivo do que o limiar geral que apenas sinaliza ambiguidade.
- **FR-007**: O sistema MUST tratar o reprocessamento do mesmo documento como operação idempotente também após a correção do runtime, evitando duplicação de documentos, transações, vínculos parcelados e projeções.
- **FR-008**: O sistema MUST manter disponíveis as consultas por mês, cartão, compra, parcela e saldo futuro sem exigir ao usuário conhecimento sobre mudanças internas no caminho de execução.
- **FR-009**: O sistema MUST deixar explícito quando um documento suportado não pôde completar o fluxo oficial corrigido, preservando contexto suficiente para diagnóstico e ação operacional.
- **FR-009a**: O sistema MUST persistir tudo que for possível com marcação explícita de incompletude quando a falha ocorrer após o início do workflow, desde que a origem e o estado parcial permaneçam auditáveis.
- **FR-010**: O sistema MUST permitir evolução de cobertura para novos emissores e layouts sem reintroduzir caminhos paralelos que contornem o fluxo oficial prometido.
- **FR-010a**: O sistema MUST invalidar resultados históricos produzidos pelo runtime legado e impedir seu uso em consultas operacionais ou analíticas até que sejam reconstruídos manualmente sob o fluxo oficial corrigido.
- **FR-011**: O sistema MUST garantir que valores observados em faturas processadas e valores projetados para competências futuras permaneçam separados em toda resposta operacional ou analítica exposta ao usuário.
- **FR-012**: O sistema MUST fornecer um meio verificável para que mantenedores confirmem que a aderência entre arquitetura aprovada e comportamento de runtime foi restabelecida para o fluxo principal.

### Key Entities *(include if feature involves data)*

- **Execução Oficial de Ingestão**: Representa uma execução completa do pipeline principal de faturas, com etapas observáveis, estado de progresso e resultado final auditável.
- **Etapa de Runtime**: Representa uma fase relevante do fluxo oficial, com entrada, saída, decisão associada e evidência operacional.
- **Pendência de Interpretação**: Representa um ponto do processamento que não pode ser aceito automaticamente e exige revisão humana antes da conclusão completa.
- **Decisão Assistida Elegível**: Representa um ponto ambíguo em que o agente de IA está autorizado a decidir e aplicar a resolução dentro do workflow oficial.
- **Resultado Estruturado da Fatura**: Representa o conjunto persistido de metadados, lançamentos, parcelamentos, projeções e decisões disponível para consulta posterior.
- **Evidência de Aderência**: Representa o registro operacional que comprova que determinada transformação ocorreu dentro do fluxo oficial prometido.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das execuções bem-sucedidas de uma fatura suportada, o mantenedor consegue identificar no próprio produto que a extração principal, a coordenação do fluxo e a persistência ocorreram dentro do runtime oficial.
- **SC-002**: Após a correção, o reprocessamento do mesmo documento mantém taxa de duplicação indevida igual a 0% para documentos, transações, vínculos parcelados e projeções previamente reconhecidos.
- **SC-003**: Em um conjunto representativo de faturas suportadas, pelo menos 95% das execuções concluídas preservam a capacidade de responder consultas por mês, cartão, compra, parcela e saldo futuro sem intervenção manual adicional além da revisão já prevista para itens ambíguos.
- **SC-004**: 100% dos documentos que não concluírem o fluxo oficial corrigido geram contexto suficiente para que um mantenedor entenda em menos de 5 minutos por que a execução não aderiu ao caminho esperado.
- **SC-004a**: 100% das persistências parciais mantêm marcação explícita de incompletude e contexto suficiente para retomada ou diagnóstico posterior.
- **SC-005**: Um mantenedor consegue verificar a restauração da aderência entre arquitetura aprovada e comportamento real do pipeline em uma única execução observável do produto, sem depender de interpretação manual de documentação paralela.
- **SC-006**: 100% das decisões autoaplicadas pelo agente de IA exibem evidência auditável do limiar alto específico usado para elegibilidade.
- **SC-007**: 100% dos dados legados invalidados ficam claramente indisponíveis para consulta até reconstrução manual confirmada.

## Assumptions

- A proposta funcional da `001-invoice-extractor` continua válida; esta feature corrige a aderência de runtime do fluxo principal sem redefinir os objetivos de negócio já aprovados para ingestão, consulta e persistência.
- O diagnóstico produzido em `002-usage-report` é tratado como evidência de lacuna atual e como insumo para validar que a correção realmente removeu o desvio identificado.
- A v1 continua priorizando faturas de cartão pessoais já suportadas pelo projeto antes de expandir cobertura para novos emissores ou novas classes documentais.
- Itens ambíguos elegíveis podem ser decididos e aplicados automaticamente pelo agente de IA; os demais continuam seguindo para revisão humana.
- A autoaplicação pelo agente de IA só é permitida acima de um limiar alto específico de confiança, mais restritivo do que o limiar geral de ambiguidade.
- Em falhas ocorridas depois do início do workflow, a solução deve preferir persistência parcial auditável a descarte completo do progresso obtido.
- A base canônica consolidada e as consultas operacionais já prometidas ao usuário precisam permanecer estáveis durante a correção da aderência arquitetural.
- Fallback legado baseado em sidecars preparados fora do runtime oficial fica explicitamente fora de escopo desta correção.
- Resultados históricos gerados pelo runtime legado deixam de ser válidos para consulta e exigem reconstrução manual no fluxo novo antes de qualquer reutilização.
