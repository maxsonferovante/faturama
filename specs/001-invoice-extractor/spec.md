# Feature Specification: Extrator de Faturas Estruturadas

**Feature Branch**: `[001-invoice-extractor]`

**Created**: 2026-06-27

**Status**: Draft

**Input**: User description: "Construir um pipeline para transformar faturas de cartão em dados estruturados, consultáveis por mês, cartão, compra, parcela e saldo futuro, com separação clara entre extração, interpretação assistida e persistência."

## Clarifications

### Session 2026-06-27

- Q: Qual deve ser a superfície inicial de uso da v1? → A: CLI para ingestão, consultas e revisão operacional.
- Q: Como a v1 deve tratar itens abaixo do limiar de confiança? → A: Sempre abrir fila de revisão para itens abaixo do limiar.
- Q: Qual deve ser a base canônica inicial da v1? → A: SQLite como base canônica inicial.
- Q: A v1 deve modelar categorias detalhadas de gasto? → A: Não modelar categorias de gasto detalhadas na v1.
- Q: Como a v1 deve definir a identidade canônica de uma compra parcelada? → A: Descrição normalizada + valor da parcela + cartão + data de origem aproximada.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Processar faturas sem perder rastreabilidade (Priority: P1)

Como usuário, quero adicionar uma ou mais faturas e receber cada fatura convertida em registros estruturados e auditáveis para que eu possa confiar no resultado e reaproveitá-lo em consultas futuras.

**Why this priority**: Sem ingestão confiável e rastreável, o sistema não entrega valor analítico nem base segura para revisão e reprocessamento.

**Independent Test**: Pode ser testada processando uma fatura suportada e verificando que a competência, o cartão, os totais básicos e os lançamentos relevantes ficam disponíveis com vínculo à origem documental.

**Acceptance Scenarios**:

1. **Given** uma fatura suportada ainda não processada, **When** o usuário a adiciona ao sistema, **Then** o sistema registra a fatura, identifica seus metadados principais e persiste os lançamentos financeiros com referência à origem.
2. **Given** uma fatura com lançamentos parcelados e lançamentos não financeiros no mesmo documento, **When** o processamento é concluído, **Then** o sistema separa apenas os lançamentos relevantes e mantém evidências suficientes para auditoria posterior.

---

### User Story 2 - Consultar gastos e parcelas por competência e cartão (Priority: P2)

Como usuário, quero consultar gastos do mês, parcelas cobradas e saldo parcelado futuro por cartão para entender o que já foi cobrado e o que ainda está comprometido nas próximas competências.

**Why this priority**: O principal resultado de negócio da extração é responder perguntas mensais sobre gastos correntes e compromissos futuros.

**Independent Test**: Pode ser testada com faturas consecutivas do mesmo cartão, verificando que o sistema diferencia compras novas, parcelas do mês e projeções futuras em consultas por competência.

**Acceptance Scenarios**:

1. **Given** faturas consecutivas já processadas do mesmo cartão, **When** o usuário consulta os gastos de uma competência, **Then** o sistema informa o total do mês por cartão e separa compras novas, parcelas cobradas e demais ajustes financeiros.
2. **Given** um plano parcelado identificado em uma fatura anterior, **When** o usuário consulta parcelas do próximo mês, **Then** o sistema retorna as parcelas previstas e o saldo parcelado remanescente por cartão.

---

### User Story 3 - Revisar ambiguidades e reprocessar com segurança (Priority: P3)

Como usuário, quero identificar itens ambíguos, corrigi-los e reprocessar a mesma fatura sem duplicações para que a base canônica melhore com o tempo sem perder consistência histórica.

**Why this priority**: Ambiguidade documental é inevitável; o sistema precisa tratá-la de forma operacional sem corromper a base de dados.

**Independent Test**: Pode ser testada processando uma fatura com itens de baixa confiança, registrando pendências de revisão, retomando o fluxo após ajuste e confirmando que o reprocessamento não duplica registros.

**Acceptance Scenarios**:

1. **Given** uma fatura com itens de interpretação ambígua, **When** o sistema detecta baixa confiança, **Then** ele preserva os dados confiáveis, registra os itens pendentes e permite retomada do processamento a partir do ponto de revisão.
2. **Given** uma fatura já processada anteriormente, **When** o usuário solicita novo processamento do mesmo arquivo, **Then** o sistema atualiza o resultado de forma idempotente sem duplicar transações nem projeções já conhecidas.

### Edge Cases

- O que acontece quando a fatura não traz uma seção explícita de próximas parcelas, mas contém parcelas identificáveis nas linhas do extrato?
- Como o sistema lida com descrições variantes do mesmo lojista entre competências consecutivas?
- Como o sistema trata estorno parcial, ajuste ou pagamento que possam se parecer com uma compra comum?
- Como o sistema responde quando o mesmo cartão possui titular e adicional misturados na mesma fatura?
- Como o sistema mantém precisão quando datas, valores ou descrições vêm truncados ou quebrados em múltiplas linhas?
- Como o sistema evita projeções incorretas quando a competência da compra difere da competência da cobrança?
- Como o sistema sinaliza incerteza quando há moeda internacional, OCR imperfeito ou evidência insuficiente?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST aceitar uma ou mais faturas de cartão por usuário e registrar cada documento processado como uma competência rastreável por cartão.
- **FR-002**: O sistema MUST extrair, quando presentes, os metadados essenciais da fatura, incluindo emissor, identificação do cartão, competência, datas relevantes e totais principais.
- **FR-003**: O sistema MUST identificar quais linhas representam lançamentos financeiros relevantes e separar conteúdos promocionais, explicativos ou auxiliares.
- **FR-004**: O sistema MUST classificar cada lançamento financeiro em categorias operacionais distintas, incluindo compras novas, parcelas cobradas, pagamentos, estornos, ajustes, encargos e parcelamento da própria fatura.
- **FR-005**: O sistema MUST identificar compras parceladas e consolidar ocorrências mensais compatíveis em um único plano parcelado por cartão, usando como chave canônica inicial a combinação de descrição normalizada, valor da parcela, cartão e data de origem aproximada.
- **FR-006**: O sistema MUST projetar as parcelas futuras restantes de cada plano parcelado identificado sempre que houver evidência suficiente para isso.
- **FR-007**: O sistema MUST calcular agregados por competência e cartão que permitam responder, no mínimo, total do mês, total de parcelas cobradas, saldo parcelado futuro e composição do gasto por categoria de lançamento.
- **FR-008**: O sistema MUST manter rastreabilidade entre cada registro estruturado e sua evidência de origem, incluindo ao menos arquivo de origem, página, texto bruto, estratégia de extração utilizada e nível de confiança.
- **FR-009**: O sistema MUST registrar um nível de confiança por entidade relevante e encaminhar todo item abaixo do limiar configurado para fila de revisão manual, distinguindo entre itens aceitos automaticamente, itens persistidos com pendência e itens que exigem revisão manual.
- **FR-010**: O sistema MUST permitir retomada do processamento a partir de pendências de revisão sem exigir o reprocessamento integral do documento.
- **FR-011**: O sistema MUST tratar o reprocessamento do mesmo arquivo como operação idempotente, evitando duplicação de documentos, transações, vínculos parcelados e projeções.
- **FR-012**: O sistema MUST preservar separação clara entre dados observados em faturas já processadas e valores projetados para competências futuras.
- **FR-013**: O sistema MUST disponibilizar, na v1, uma interface de linha de comando por usuário, competência e cartão para listar faturas processadas, transações de uma fatura, compras novas do mês, parcelas do mês, parcelas futuras conhecidas e saldo parcelado remanescente.
- **FR-014**: O sistema MUST manter histórico suficiente de decisões para explicar por que uma transação, vínculo parcelado ou projeção foi aceita, rejeitada ou enviada para revisão.
- **FR-015**: O sistema MUST permitir evolução gradual para novos emissores sem alterar a semântica do modelo canônico já persistido.
- **FR-016**: O sistema MUST usar SQLite como base canônica inicial para persistir documentos, faturas, transações, planos parcelados, projeções, itens de revisão e registros de decisão da v1.
- **FR-017**: O sistema MUST priorizar na v1 a estrutura financeira bruta dos lançamentos e vínculos parcelados, sem exigir categorização detalhada de gastos por tipo de comércio.

### Key Entities *(include if feature involves data)*

- **Fatura Processada**: Representa o documento mensal de cartão com competência, cartão, totais principais, estado de processamento e vínculo com o arquivo de origem.
- **Lançamento Financeiro**: Representa cada ocorrência financeira relevante extraída da fatura, com datas, descrição, valor, tipo operacional, confiança e evidências de origem.
- **Plano Parcelado**: Representa uma compra parcelada consolidada ao longo do tempo, reunindo as ocorrências mensais da mesma obrigação financeira.
- **Projeção Futura**: Representa cada parcela ainda não cobrada, prevista a partir de um plano parcelado conhecido.
- **Resumo Mensal por Cartão**: Representa os totais consolidados por competência e cartão usados para consultas analíticas recorrentes.
- **Item de Revisão**: Representa uma pendência operacional aberta quando a confiança ou a consistência dos dados não permite aceitação automática segura.
- **Registro de Decisão**: Representa a justificativa auditável para aceitação, rejeição, consolidação ou encaminhamento para revisão de cada entidade relevante.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em uma fatura suportada, o sistema produz uma fatura estruturada com competência, cartão e totais principais preenchidos em pelo menos 95% dos documentos processados sem intervenção manual.
- **SC-002**: Em um conjunto de faturas consecutivas do mesmo cartão, pelo menos 90% das parcelas explicitamente identificadas no documento são agrupadas corretamente em seus respectivos planos parcelados.
- **SC-003**: O usuário consegue responder, para qualquer competência processada, quanto gastou por cartão e quais parcelas vencem no mês em menos de 1 minuto a partir da consulta aos dados já persistidos.
- **SC-004**: O reprocessamento do mesmo arquivo mantém taxa de duplicação indevida igual a 0% para documentos, transações e projeções previamente reconhecidos.
- **SC-005**: Pelo menos 95% dos itens enviados para revisão manual incluem evidência suficiente para que um revisor entenda a origem do problema sem reabrir o documento inteiro.
- **SC-006**: O sistema diferencia valores observados e valores projetados em 100% das respostas analíticas expostas ao usuário.

## Assumptions

- A primeira versão foca em faturas de cartão de crédito pessoais e não inclui outros produtos financeiros como boletos, empréstimos, seguros, cashback ou programas de pontos.
- O sistema pode operar inicialmente com um conjunto conhecido de emissores e expandir cobertura progressivamente sem redefinir o modelo canônico das consultas.
- Categorias de gasto detalhadas por tipo de comércio ficam explicitamente fora do escopo da v1 e poderão ser adicionadas depois da estabilização da estrutura financeira bruta e dos vínculos parcelados.
- Todo item abaixo do limiar configurado de confiança deve entrar em fila de revisão manual, mesmo quando o restante da fatura puder seguir com persistência parcial segura.
- A base canônica da v1 precisa atender consultas operacionais e analíticas para um único histórico consolidado por usuário, sem exigir colaboração multiusuário em tempo real.
- A superfície inicial de uso da v1 será uma CLI para processamento, consulta e revisão operacional, deixando API e interface web para fases posteriores.
- A v1 usará SQLite como base canônica local antes de qualquer evolução para banco servidor ou armazenamento analítico adicional.
- A identidade canônica inicial de compras parceladas combinará descrição normalizada, valor da parcela, cartão e data de origem aproximada, antes de qualquer matching histórico mais sofisticado.
