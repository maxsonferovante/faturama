# Research: PostgreSQL Only Persistence

## Decision 1: Remover SQLite por subtração arquitetural, não por camada de compatibilidade adicional

**Decision**: A refatoração deve começar apagando `src/faturama/infrastructure/database/sqlite.py`, removendo o fallback `connect(settings.database_path)` e eliminando a aceitação de DSNs `sqlite:///`, extensões `.sqlite3` e `.db` do caminho produtivo.

**Rationale**: O estado atual mantém dois modelos mentais conflitantes: PostgreSQL como backend oficial do worker local e SQLite como semântica dominante do código. A camada `postgres.py` adapta SQL legado em vez de representar uma infraestrutura PostgreSQL nativa. Continuar expandindo compatibilidade só perpetua acoplamento e falsos positivos.

**Alternatives considered**:

- **Manter um adapter híbrido SQLite/PostgreSQL**: descartado porque contraria a decisão arquitetural de banco único e continua mascarando bugs de dialeto.
- **Marcar SQLite como “somente legacy” mas mantê-lo no runtime**: descartado porque a simples presença do fallback permite regressão silenciosa.

## Decision 2: Centralizar conexão, transação e lifecycle em uma Unit of Work PostgreSQL explícita

**Decision**: A aplicação deve passar a depender de uma fábrica/unidade de trabalho PostgreSQL-only que abra conexão `psycopg` com `row_factory=dict_row`, coordene transação atômica e exponha repositórios e serviços de checkpoint/read model já montados.

**Rationale**: Hoje `process_invoice` e `process_processing_command` montam infraestrutura concreta dentro do use case e cada repositório chama `commit()` por conta própria. Isso impede rollback consistente quando documento, statements, transações, projeções, review e decisão precisam ser persistidos como uma única operação lógica.

**Alternatives considered**:

- **Continuar abrindo conexão em cada use case**: descartado porque mantém acoplamento de aplicação com infraestrutura e lifecycle disperso.
- **Criar um service locator genérico multi-banco**: descartado porque adiciona abstração sem necessidade; o alvo é um único backend oficial.

## Decision 3: Trocar SQL legado SQLite por SQL PostgreSQL nativo e contratos mínimos de porta

**Decision**: Os repositórios concretos devem ser reescritos para SQL PostgreSQL explícito, usando `INSERT ... ON CONFLICT ... DO UPDATE`, placeholders do `psycopg`, `BOOLEAN` para flags binárias e contratos mínimos em `application/ports` para unidade de trabalho, checkpoint store, query/read service e repositórios necessários.

**Rationale**: O código produtivo atual ainda usa `INSERT OR REPLACE`, placeholders `?`, tipos `sqlite3.Connection`, `PRAGMA` e leitura direta de `repo.connection.execute(...)`. Esses sinais mostram que a aplicação está acoplada ao dialeto legado.

**Alternatives considered**:

- **Adaptar SQL em runtime por regex**: descartado porque esconde diferenças semânticas importantes e dificulta manutenção.
- **Mover tudo para ORM completo agora**: descartado porque aumenta escopo; a necessidade atual é remover SQLite com a menor abstração adicional possível.

## Decision 4: Substituir bootstrap dinâmico por migração versionada ou DDL PostgreSQL explícito no bootstrap

**Decision**: `schema.py` deve deixar de usar `sqlite3.Connection`, `PRAGMA table_info` e `_apply_compatibility_migrations` como estratégia principal. O plano alvo é um bootstrap PostgreSQL explícito, preferencialmente por migrações versionadas sob `infrastructure/database/migrations/`; se isso não entrar inteiro na primeira fatia, o mínimo aceitável é DDL PostgreSQL nativo e idempotente executado por bootstrap controlado.

**Rationale**: Evolução de schema em tempo de conexão, baseada em introspecção ad hoc, é frágil e pouco previsível em ambiente compartilhado. A feature exige previsibilidade de deploy/bootstrap e abandono completo da semântica SQLite.

**Alternatives considered**:

- **Continuar com `_apply_compatibility_migrations`**: descartado porque mantém mutação oportunista e runtime-dependent.
- **Adiar qualquer formalização de schema**: descartado porque a remoção de SQLite exige redefinir o contrato de bootstrap imediatamente.

## Decision 5: Persistir checkpoints no mesmo PostgreSQL oficial e remover o runtime SQLite do LangGraph

**Decision**: `postgres_checkpoint.py` e `langgraph_checkpoint.py` devem ser substituídos por uma implementação PostgreSQL real para `workflow_checkpoints`, com operações explícitas de `save`, `latest`, `mark_restored` e integração do runtime de workflow sem `langgraph.checkpoint.sqlite` nem `langgraph-checkpoint-sqlite`.

**Rationale**: O código atual anuncia PostgreSQL, mas grava checkpoints em `data/faturama-async-checkpoints.sqlite3` quando o DSN não é SQLite. Isso viola o requisito funcional e cria um segundo backend invisível ao operador.

**Alternatives considered**:

- **Manter `SqliteSaver` apenas para checkpoints**: descartado porque continua produzindo dualidade operacional.
- **Eliminar checkpointing completamente**: descartado porque a feature precisa preservar retomada e `review_required`.

## Decision 6: Transformar queries e CLI em composição orientada a portas, usando o mesmo DSN oficial do processamento

**Decision**: As queries de aplicação deixam de aceitar `database_path` e passam a receber um read service ou portas de leitura montadas pela borda de interface. A CLI deixa de resolver `_db_path()` por `load_settings().database_path` e passa a usar a mesma composição PostgreSQL oficial do restante da aplicação.

**Rationale**: Hoje `list_transactions`, `list_statements`, `monthly_spend`, `current_installments`, `future_installments`, `show_statement`, `remaining_balance`, `review_queue` e `resolve_review` carregam ou propagam caminho de arquivo local. Isso quebra a ideia de banco único e impede reuso do lifecycle/transação centralizados.

**Alternatives considered**:

- **Trocar apenas `connect(Path(...))` por `connect_from_dsn(...)` nas queries**: descartado porque preserva acoplamento entre camada de aplicação e infraestrutura.
- **Resolver DSN em variáveis globais dentro dos módulos de query**: descartado porque só troca um acoplamento por outro.

## Decision 7: Migrar testes e documentação para o ambiente local oficial baseado em Docker Compose

**Decision**: Os fixtures `.sqlite3`, `FATURAMA_DB_PATH`, `FATURAMA_CHECKPOINT_DB_PATH` e `FATURAMA_DB_DSN=sqlite:///...` devem ser removidos dos testes e substituídos por PostgreSQL real em container, reutilizando o `docker-compose.yml` oficial ou estratégia equivalente de container efêmero. README, runbooks, docs de schema e specs ativas devem ser atualizados para PostgreSQL único.

**Rationale**: O `docker-compose.yml` já declara `postgres:16-alpine` e o worker já usa `FATURAMA_DB_DSN=postgresql://faturama:faturama@postgres:5432/faturama`. O que falta é alinhar CLI, suíte local e documentação ao mesmo contrato.

**Alternatives considered**:

- **Preservar SQLite nos testes por velocidade**: descartado porque a suíte atual mascara justamente os problemas que a feature precisa expor.
- **Atualizar só README e deixar runbooks/specs antigos**: descartado porque continuaria reintroduzindo arquitetura errada no uso diário.
