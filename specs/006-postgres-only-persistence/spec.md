# Feature Specification: PostgreSQL Only Persistence

**Feature Branch**: `[006-postgres-only-persistence]`

**Created**: 2026-06-29

**Status**: Draft

**Input**: User description: "Analisei o repositório maxsonferovante/faturama com foco na remoção completa da dualidade SQLite/PostgreSQL. A conclusão técnica é: o PostgreSQL já existe no runtime local/worker, mas o código ainda foi escrito majoritariamente com semântica SQLite e depois adaptado via camada de compatibilidade. Isso precisa ser removido, não expandido."

## User Scenarios & Testing

### User Story 1 - Processar faturas com banco único (Priority: P1)

Como responsável pela operação do faturama, quero que todo processamento de fatura use apenas o banco transacional oficial para que os dados canônicos e o estado operacional não dependam de arquivos locais ou caminhos alternativos.

**Why this priority**: Esse é o fluxo principal do produto e hoje ainda há divergência entre o caminho síncrono, o worker assíncrono e a persistência de checkpoints.

**Independent Test**: Pode ser testado executando o processamento de uma fatura com a configuração oficial do banco e verificando que documentos, statements, evidências, transações, parcelas, projeções, resumos, revisões, decisões e checkpoints são gravados no mesmo backend oficial, sem criação nem leitura de arquivos locais de banco.

**Acceptance Scenarios**:

1. **Given** uma configuração válida do banco oficial, **When** uma fatura é processada pelo fluxo principal, **Then** todos os dados canônicos e operacionais do processamento são persistidos no backend oficial e nenhum arquivo local de banco é necessário.
2. **Given** uma execução assíncrona retomada após interrupção, **When** o workflow recupera seu último estado, **Then** a retomada usa o mesmo backend oficial e preserva criação, leitura e marcação de restauração de checkpoints.
3. **Given** um item que exige revisão manual, **When** o processamento entra em `review_required`, **Then** a retomada e a fila de revisão continuam funcionais sem depender de persistência local.

---

### User Story 2 - Consultar dados operacionais pela CLI sem caminhos locais (Priority: P2)

Como usuário da CLI, quero consultar transações, faturas, gastos mensais, parcelas correntes, parcelas futuras, detalhes de statement e saldo remanescente a partir da infraestrutura oficial para que as consultas reflitam o mesmo banco usado pelo processamento.

**Why this priority**: A utilidade operacional da CLI depende de ler o mesmo estado persistido pelo pipeline, sem divergência entre banco de processamento e banco de consulta.

**Independent Test**: Pode ser testado processando dados pelo fluxo oficial e executando cada comando de leitura da CLI sem informar caminho de arquivo, validando que as respostas são obtidas do backend oficial configurado via DSN.

**Acceptance Scenarios**:

1. **Given** dados já persistidos no backend oficial, **When** o usuário executa um comando de consulta da CLI, **Then** a resposta é retornada a partir da configuração oficial do banco e não exige `database_path`.
2. **Given** uma configuração inválida ou ausente do banco oficial, **When** o usuário executa um comando de consulta da CLI, **Then** a CLI falha explicitamente com erro de configuração em vez de buscar um banco local alternativo.

---

### User Story 3 - Operar com contrato de configuração único e confiável (Priority: P3)

Como mantenedor do sistema, quero um contrato de configuração e testes alinhado a um único banco transacional para que incompatibilidades com o ambiente real apareçam cedo e a documentação não reintroduza a arquitetura antiga.

**Why this priority**: Configuração, testes e documentação ainda normalizam a dualidade antiga e mascaram regressões importantes de compatibilidade.

**Independent Test**: Pode ser testado inicializando a aplicação e a suíte relevante com variáveis oficiais do banco, verificando falha rápida quando o DSN obrigatório não existe e confirmando que quickstarts, runbooks, README e specs ativos não recomendam SQLite.

**Acceptance Scenarios**:

1. **Given** o ambiente sem DSN obrigatório, **When** a aplicação ou o worker são iniciados, **Then** a inicialização falha rapidamente com mensagem de configuração ausente ou inválida.
2. **Given** a suíte de testes e a documentação atualizadas, **When** o projeto é validado para uso local e assíncrono, **Then** testes, quickstarts e runbooks exercitam e descrevem somente o banco oficial.

### Edge Cases

- Como o sistema se comporta quando o DSN está presente mas aponta para um esquema não suportado pelo contrato oficial.
- Como o processamento reage quando um retry assíncrono precisa restaurar checkpoint após falha parcial sem qualquer artefato local persistido.
- Como a CLI deve responder quando o banco oficial está indisponível no momento da consulta.
- Como a migração lida com dados e documentação legados que ainda assumem caminhos `*.sqlite3` e variáveis de ambiente antigas.

## Requirements

### Functional Requirements

- **FR-001**: O sistema MUST operar com um único banco transacional oficial configurado via DSN obrigatório para todos os fluxos síncronos, assíncronos e de leitura operacional.
- **FR-002**: O sistema MUST remover suporte a persistência local em SQLite, arquivos `*.sqlite3` e qualquer fallback baseado em `FATURAMA_DB_PATH`.
- **FR-003**: O caso de uso principal de processamento de faturas MUST falhar explicitamente quando a configuração oficial do banco estiver ausente ou inválida, em vez de abrir um banco local alternativo.
- **FR-004**: O processamento de faturas MUST persistir documentos, statements, evidências, transações, parcelas, projeções, resumos, revisões e decisões somente no banco transacional oficial.
- **FR-005**: O fluxo assíncrono MUST usar o mesmo backend transacional oficial adotado pelo restante da aplicação, sem camada de compatibilidade que reintroduza semântica SQLite.
- **FR-006**: O caso de uso de processamento de comandos assíncronos MUST falhar rapidamente quando o DSN obrigatório do banco oficial não estiver configurado.
- **FR-007**: As consultas de leitura `list_transactions`, `list_statements`, `monthly_spend`, `current_installments`, `future_installments`, `show_statement` e `remaining_balance` MUST ler do banco oficial por meio da infraestrutura configurada por DSN, sem receber caminho de arquivo como contrato principal.
- **FR-008**: A CLI MUST obter acesso ao banco por factory ou composição de infraestrutura alinhada ao backend oficial, sem centralizar resolução de caminho local de banco.
- **FR-009**: O mecanismo de checkpoint do workflow MUST persistir criação, leitura do último checkpoint, marcação de restauração e suporte a `review_required` sem usar SQLite.
- **FR-010**: A retomada de workflows interrompidos e o processamento de itens em revisão MUST permanecer funcionais após a remoção completa do backend SQLite.
- **FR-011**: O contrato de configuração MUST expor apenas variáveis do banco oficial e tratar o DSN como obrigatório, rejeitando esquemas fora do contrato aceito.
- **FR-012**: Os testes automatizados MUST exercitar o comportamento com o banco oficial e deixar de mascarar incompatibilidades por meio de bancos temporários SQLite ou DSNs `sqlite:///`.
- **FR-013**: README, quickstarts, runbooks, docs de schema, specs ativas e arquivos de refinamento MUST deixar de recomendar ou descrever SQLite como opção suportada.
- **FR-014**: O sistema MUST produzir erros operacionais claros quando o banco oficial estiver indisponível, para que operadores não interpretem a falha como ausência de dados locais.
- **FR-015**: A feature MUST tratar dados SQLite legados como fora do runtime suportado após a migração, registrando explicitamente se serão descartados, ignorados como histórico inválido ou migrados por procedimento separado, sem fallback automático no código produtivo.

### Key Entities

- **Banco Transacional Oficial**: Fonte única de verdade para dados canônicos e estado operacional do pipeline, acessada por configuração obrigatória baseada em DSN.
- **Documento Processado**: Registro da entrada de fatura e de sua identidade canônica, associado a statements, evidências e resultados de processamento.
- **Checkpoint de Workflow**: Estado persistido necessário para retomar execuções interrompidas, suportar revisões pendentes e registrar restaurações.
- **Read Model Operacional**: Conjunto de visões consultadas pela CLI para faturas, transações, gastos, parcelas e saldos, derivadas do mesmo banco oficial do processamento.
- **Contrato de Configuração**: Superfície de configuração responsável por aceitar apenas o backend oficial e bloquear parâmetros legados de persistência local.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% dos fluxos oficiais de processamento e consulta executam sem exigir caminho de arquivo de banco local.
- **SC-002**: 100% das inicializações sem DSN obrigatório falham antes do processamento com erro explícito de configuração.
- **SC-003**: 100% dos cenários de retomada de workflow e `review_required` validados para a feature usam o mesmo backend oficial do restante da aplicação.
- **SC-004**: 100% dos testes atualizados para esta feature deixam de usar SQLite ou DSNs `sqlite:///` como backend aceito.
- **SC-005**: 100% da documentação operacional revisada para esta feature descreve um único banco transacional oficial para desenvolvimento local e runtime assíncrono, considerando no mínimo `README.md`, `docs/`, specs ativas e refinamentos explicitamente mantidos no repositório.

## Assumptions

- O banco transacional oficial já é o backend alvo aceito pelo runtime local e pelo worker, e a feature remove apenas os caminhos legados que mantêm a dualidade.
- A semântica de dados canônicos existente para documentos, statements, transações, parcelamentos, projeções, revisões e decisões deve ser preservada durante a consolidação do backend.
- Ambientes locais e de automação conseguirão provisionar o banco oficial de forma repetível para desenvolvimento, testes e execução assíncrona.
- A remoção de SQLite inclui código de aplicação, configuração, testes e documentação, mesmo quando algumas referências estiverem em specs ou runbooks históricos ainda tratados como material ativo.
- Dados persistidos anteriormente em SQLite não serão usados como fallback em runtime; qualquer tratamento desses dados deverá ser documentado explicitamente como descarte, invalidação histórica ou migração separada.
