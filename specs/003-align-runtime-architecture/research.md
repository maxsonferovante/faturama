# Research: Alinhamento de Runtime da Arquitetura

## Decision 1: LangGraph será a orquestração oficial do pipeline

**Decision**: O fluxo principal de ingestão passará a ser construído como um `StateGraph` compilado, com nós explícitos para extração, parsing estrutural, resolução de ambiguidade, persistência e materialização de checkpoints.

**Rationale**: A documentação oficial do LangGraph posiciona `StateGraph` e `compile()` como o mecanismo de construção do workflow e de suas transições. Isso fecha o desvio atual, no qual existe apenas um helper local de checkpoints sem um grafo real coordenando o runtime.

**Alternatives considered**:

- **Manter orquestração manual em função linear**: descartado porque preserva a lacuna entre arquitetura prometida e runtime real.
- **Criar um motor de estados próprio**: descartado por reinventar responsabilidade já coberta pela biblioteca que a arquitetura prometeu usar.

## Decision 2: Revisão assistida usará `interrupt` e checkpoints SQLite

**Decision**: Casos ambíguos ou abaixo do limiar de confiança entrarão em um ramo de revisão do grafo que pode pausar com `interrupt`, persistir checkpoint e retomar depois com resolução de IA ou humana, sempre com payload serializável e side effects idempotentes.

**Rationale**: A documentação oficial do LangGraph recomenda tratar `interrupt` como pausa real de execução, evitar encapsulá-lo em `try/except`, manter a ordem das interrupções estável e garantir idempotência antes de pontos de pausa. A documentação de checkpointers também oferece implementação SQLite apropriada para workflow local.

**Alternatives considered**:

- **Continuar com fila manual fora do workflow**: descartado porque deixa a revisão desconectada do runtime oficial.
- **Usar IA sem pausa nem checkpoint**: descartado porque reduz auditabilidade e dificulta retomada segura.
- **Checkpoints em arquivo JSON ad hoc**: descartado porque não usa a infraestrutura oficial da biblioteca e complica histórico/resume.

## Decision 3: `OpenDataLoader PDF` será a extração primária canônica

**Decision**: O adaptador oficial de extração chamará `opendataloader_pdf.convert(...)` para gerar artefatos Markdown e JSON a partir do PDF de entrada, tratando esses artefatos como produtos do runtime e não mais como pré-requisito externo.

**Rationale**: O repositório oficial do `opendataloader-pdf` documenta `convert(...)` como a forma Python suportada para produzir saída local em Markdown/JSON e destaca que a chamada pode processar lotes, evitando custo repetido de subir JVM por arquivo individual.

**Alternatives considered**:

- **Continuar resolvendo sidecars locais por convenção de nome**: descartado porque isso apenas consome artefatos pré-gerados e não integra a extração real ao runtime.
- **Trocar para outro parser de PDF**: descartado porque a arquitetura e a spec já definiram `OpenDataLoader` como responsabilidade primária de extração.

## Decision 4: A integração LangChain `OpenDataLoaderPDFLoader` será usada no ramo de IA

**Decision**: O componente `OpenDataLoaderPDFLoader` será usado para carregar o PDF como `Document` estruturado apenas no ramo assistido por IA, onde o agente precisa de contexto semântico por página para revisar casos ambíguos, enquanto a persistência canônica continua ancorada na extração primária do `opendataloader_pdf`.

**Rationale**: A documentação do LangChain descreve `OpenDataLoaderPDFLoader` como um loader que converte o PDF em `Document` com `page_content` e metadados por página, incluindo formatos `markdown` e `json`. Isso combina bem com o objetivo de dar contexto ao agente sem transformar a IA em fonte primária da verdade.

**Alternatives considered**:

- **Usar o loader LangChain como extrator canônico único**: descartado porque o fluxo precisa continuar produzindo artefatos persistíveis e auditáveis próprios do pipeline.
- **Não usar a integração LangChain**: descartado porque o usuário pediu explicitamente o uso dessa integração e ela resolve bem o fornecimento de contexto ao agente de revisão.

## Decision 5: Sidecars passam de entrada obrigatória para cache/output do pipeline

**Decision**: Markdown e JSON deixam de ser dependência externa obrigatória do `process-invoice` e passam a ser artefatos gerados, reutilizados e invalidados pelo próprio runtime oficial.

**Rationale**: Isso mantém compatibilidade com a rastreabilidade já existente no modelo canônico, mas remove o desvio estrutural no qual o sistema só funciona se outra etapa tiver preparado arquivos auxiliares antes da execução principal.

**Alternatives considered**:

- **Eliminar totalmente artefatos intermediários**: descartado porque reduz explicabilidade e dificulta auditoria local.
- **Persistir somente texto bruto no banco**: descartado porque perde a relação direta com a extração primária e com dados estruturais por página.

- **Confiar apenas em testes unitários e integração**: descartado porque isso não evidencia sozinho o fechamento do desvio arquitetural sem checagens de comportamento observável.

## Source References

- LangGraph quickstart: `https://docs.langchain.com/oss/python/langgraph/quickstart`
- LangGraph interrupts: `https://docs.langchain.com/oss/python/langgraph/interrupts`
- LangGraph checkpointers: `https://docs.langchain.com/oss/python/langgraph/checkpointers`
- OpenDataLoader PDF repository: `https://github.com/opendataloader-project/opendataloader-pdf`
- LangChain OpenDataLoader PDF integration: `https://docs.langchain.com/oss/python/integrations/document_loaders/opendataloader_pdf`
