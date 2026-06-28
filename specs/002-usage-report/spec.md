# Feature Specification: Relatório de Uso

**Feature Branch**: `[002-usage-report]`

**Created**: 2026-06-27

**Status**: Draft

**Input**: User description: "Relatório de uso para explicitar quais componentes planejados estão realmente sendo usados em runtime, quais apenas permanecem declarados, e onde existem desvios entre arquitetura prometida e implementação atual."

## Clarifications

### Session 2026-06-27

- Q: Qual deve ser a entrega principal da v1 desse relatório? → A: CLI + Markdown materializado
- Q: Qual deve ser o escopo inicial da análise automática na v1? → A: Escopo focado em LangGraph, OpenDataLoader e sinais estruturais centrais do pipeline atual
- Q: Qual critério a v1 deve usar para concluir que um componente está realmente em uso? → A: Código executável que invoque a integração real, com testes podendo reforçar a evidência
- Q: Quando o relatório encontrar um desvio crítico no escopo analisado, o que a v1 deve fazer? → A: Identificar o desvio e corrigi-lo quando houver contexto suficiente para correção, mediante opt-in explícito

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publicar diagnóstico confiável do estado atual (Priority: P1)

Como mantenedor do projeto, eu quero um relatório objetivo sobre o uso real dos componentes declarados para entender imediatamente o que já está em produção e o que ainda é apenas intenção arquitetural.

**Why this priority**: Sem um diagnóstico confiável, decisões de priorização, correção e comunicação técnica continuam baseadas em suposição.

**Independent Test**: Pode ser testado executando um comando do produto que analisa a versão atual, retorna o diagnóstico sob demanda e materializa um relatório Markdown com as mesmas conclusões.

**Acceptance Scenarios**:

1. **Given** que o projeto possui componentes declarados e componentes efetivamente exercitados, **When** o comando do relatório é executado, **Then** cada componente relevante é classificado de forma inequívoca como usado em runtime, apenas declarado ou apenas representado por naming/arquitetura.
2. **Given** que existe um fluxo funcional implementado no produto, **When** o comando do relatório gera a saída operacional e o Markdown materializado, **Then** ambos deixam explícito o que já entrega valor hoje independentemente de integrações ainda não realizadas.

---

### User Story 2 - Evidenciar desvios entre especificação e implementação (Priority: P2)

Como responsável pela arquitetura, eu quero comparar a direção descrita nas especificações com o comportamento realmente entregue para identificar lacunas de aderência e orientar a próxima rodada de trabalho, começando pelos componentes prioritários já destacados no diagnóstico atual.

**Why this priority**: Depois do diagnóstico básico, o maior valor está em transformar diferenças entre plano e realidade em trabalho concreto e auditável.

**Independent Test**: Pode ser testado validando que o relatório lista desvios relevantes de comportamento, escopo ou integração e associa cada desvio a uma recomendação objetiva.

**Acceptance Scenarios**:

1. **Given** que uma especificação descreve integrações ou responsabilidades não refletidas na implementação, **When** o relatório é revisado, **Then** essas divergências aparecem com descrição clara do impacto.
2. **Given** que um componente aparece na arquitetura, mas não no comportamento observável do sistema, **When** o relatório é gerado, **Then** ele registra essa diferença como desvio e não como entrega concluída.

---

### User Story 3 - Apoiar decisão de remediação ou replanejamento (Priority: P3)

Como mantenedor, eu quero que o relatório termine em recomendações acionáveis para decidir se devo documentar o estado atual, alinhar as specs ao código ou implementar as integrações faltantes.

**Why this priority**: O relatório só vira ferramenta operacional quando ajuda a decidir o próximo passo, em vez de apenas descrever o problema.

**Independent Test**: Pode ser testado confirmando que o documento final apresenta caminhos de ação distintos e suficientes para orientar priorização imediata.

**Acceptance Scenarios**:

1. **Given** que o relatório identifica componentes não usados e desvios estruturais, **When** o leitor chega à conclusão, **Then** ele encontra opções de ação claras para documentação, análise adicional ou implementação.
2. **Given** que o relatório encontra um desvio crítico com contexto suficiente para correção segura, **When** a execução ocorre com a opção explícita de correção habilitada, **Then** o sistema registra o desvio identificado e aplica a correção correspondente no mesmo fluxo.

### Edge Cases

- Como o relatório deve tratar componentes que aparecem apenas como dependência declarada, sem evidência de uso operacional?
- Como o relatório deve tratar componentes parcialmente simulados por adapters ou convenções de nomenclatura, mas sem integração real?
- Como o relatório deve tratar fluxos funcionais que entregam valor mesmo sem usar as integrações originalmente prometidas?
- Como o relatório deve tratar evidências contraditórias entre documentação, testes e comportamento observável?
- Como o relatório deve agir quando detectar um desvio crítico, mas não houver contexto suficiente para correção automática segura?
- Como o relatório deve se comportar quando a análise gerar múltiplas correções plausíveis para o mesmo desvio?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST produzir um relatório legível por humanos descrevendo o estado real de uso dos componentes relevantes do produto.
- **FR-002**: O sistema MUST expor esse relatório por um comando operacional executável no próprio projeto.
- **FR-003**: O sistema MUST materializar a mesma análise em um arquivo Markdown persistido para revisão e versionamento.
- **FR-004**: A v1 MUST analisar prioritariamente LangGraph, OpenDataLoader e sinais estruturais centrais do pipeline atual.
- **FR-005**: O relatório MUST registrar a evidência usada para sustentar cada conclusão.
- **FR-006**: A v1 MUST considerar um componente como realmente usado apenas quando houver código executável que invoque a integração real, podendo testes reforçar essa evidência.
- **FR-007**: O relatório MUST separar explicitamente o que já está funcional no produto do que ainda não possui integração real.
- **FR-008**: O relatório MUST destacar divergências materiais entre especificação, dependências declaradas e comportamento observável.
- **FR-009**: O relatório MUST incluir recomendações acionáveis para cada divergência material identificada.
- **FR-010**: O relatório MUST permitir que mantenedores validem rapidamente se uma integração prometida é real, parcial ou inexistente.
- **FR-011**: O relatório MUST ser atualizável sem reescrever manualmente todas as conclusões anteriores.
- **FR-012**: O relatório MUST deixar claro quando uma conclusão foi confirmada por execução observável e quando foi inferida apenas por inspeção estrutural.
- **FR-013**: A v1 MUST limitar sua conclusão automática aos componentes explicitamente cobertos pelo escopo escolhido e não extrapolar conclusões globais para integrações fora desse conjunto.
- **FR-014**: Quando identificar um desvio crítico com contexto suficiente para correção segura, a v1 MUST registrar o desvio e só executar a correção no mesmo fluxo quando a opção explícita de correção estiver habilitada.
- **FR-015**: Quando identificar um desvio crítico sem contexto suficiente para correção segura, a v1 MUST registrar explicitamente a limitação e preservar a recomendação manual correspondente.
- **FR-016**: O relatório MUST emitir sinais operacionais mínimos da execução, incluindo logs estruturados, contagem de alvos analisados, contagem de desvios encontrados e contagem de correções aplicadas ou adiadas.
- **FR-017**: A v1 MUST considerar que existe contexto suficiente para correção segura apenas quando houver evidência primária com caminho e referência de linha, alvo único e determinístico de alteração, patch limitado ao escopo da feature e ausência de interpretações concorrentes plausíveis para a mesma correção.
- **FR-018**: O relatório materializado MUST organizar a saída em resumo executivo, alvos analisados, evidências, desvios e ações corretivas ou pendências manuais.

### Key Entities *(include if feature involves data)*

- **Usage Finding**: Representa uma conclusão sobre o status real de uso de um componente, incluindo classificação, resumo e impacto.
- **Evidence Record**: Representa a base que sustenta uma conclusão, como comportamento observável, artefato existente ou ausência verificável de uso.
- **Specification Deviation**: Representa uma diferença relevante entre o que foi prometido na arquitetura ou especificação e o que está disponível no produto.
- **Remediation Option**: Representa um próximo passo sugerido para documentação, correção de aderência ou implementação faltante.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O relatório permite identificar o status de uso de cada componente crítico analisado em menos de 5 minutos de leitura.
- **SC-002**: 100% dos componentes destacados no relatório possuem uma conclusão explícita e uma evidência associada.
- **SC-003**: 100% dos desvios materiais identificados possuem ao menos uma recomendação acionável associada.
- **SC-004**: Um mantenedor consegue decidir o próximo passo prioritário a partir do relatório sem precisar reler toda a base de código.
- **SC-005**: 100% das execuções bem-sucedidas do comando registram contagens operacionais mínimas de alvos, desvios e ações de correção ou follow-up.

## Assumptions

- O público principal da feature são mantenedores, arquitetos e revisores técnicos do projeto.
- O escopo inicial cobre LangGraph, OpenDataLoader e sinais estruturais centrais do pipeline atual, podendo ser expandido depois para outras integrações.
- O valor principal da v1 é transparência operacional e alinhamento entre documentação e produto, não auditoria histórica completa.
- O relatório pode conviver com o estado atual do produto sem bloquear o funcionamento já existente.
- Correções automáticas só devem ocorrer quando o contexto disponível permitir uma ação suficientemente defensável e rastreável, e apenas quando o usuário optar explicitamente por esse comportamento na execução.
