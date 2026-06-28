# Research: Relatório de Uso

## Decision 1: Implementar como comando CLI e materializar Markdown

**Decision**: A v1 será um comando CLI executável no projeto e, na mesma execução, produzirá um arquivo Markdown persistido com o mesmo diagnóstico.

**Rationale**: A CLI torna a feature operacional e testável; o Markdown garante revisão humana, versionamento e rastreabilidade das conclusões.

**Alternatives considered**:

- Relatório apenas em Markdown: descartado porque não atende o requisito de virar implementação real no produto.
- CLI sem artefato persistido: descartado porque reduz auditabilidade e revisão posterior.

## Decision 2: Escopo focado na v1

**Decision**: A análise automática da v1 cobrirá LangGraph, OpenDataLoader e sinais estruturais centrais do pipeline atual.

**Rationale**: O diagnóstico inicial já aponta esses componentes como maior fonte de desalinhamento entre plano e implementação. Restringir o escopo evita complexidade prematura e reduz falsos positivos.

**Alternatives considered**:

- Varredura ampla de qualquer dependência: descartada por ampliar demais regras, testes e risco de conclusões equivocadas.
- Escopo configurável desde o primeiro release: descartado por aumentar interface e esforço de validação sem necessidade imediata.

## Decision 3: Critério de “uso real”

**Decision**: Um componente só será classificado como “usado em runtime” quando houver código executável que invoque a integração real; testes podem reforçar a evidência, mas naming e dependência declarada sozinhos não bastam.

**Rationale**: Esse critério reduz falso positivo e alinha o diagnóstico com comportamento observável, não com intenção arquitetural.

**Alternatives considered**:

- Considerar dependência declarada como uso: descartado por produzir diagnóstico enganoso.
- Exigir prova obrigatória em todo runtime e todo teste: descartado por ser excessivamente rígido para a v1.

## Decision 4: Política para desvios críticos

**Decision**: A v1 identificará o desvio crítico e tentará corrigi-lo automaticamente apenas quando houver contexto suficiente para uma correção segura e rastreável; caso contrário, registrará a limitação e a recomendação manual.

**Rationale**: Preserva valor operacional sem transformar a feature em mecanismo arriscado de alteração automática.

**Alternatives considered**:

- Apenas reportar sem agir: descartado porque o usuário explicitou que o relatório deve virar implementação real com capacidade de corrigir quando fizer sentido.
- Interromper na primeira divergência: descartado porque reduz o valor diagnóstico completo da execução.

## Decision 5: Estratégia técnica da análise

**Decision**: A v1 usará leitura do checkout local, busca estrutural por imports/uso executável, inspeção de contratos e comparação com documentação da spec ativa.

**Rationale**: O problema é intrinsecamente local ao repositório e não exige integração externa para gerar valor inicial.

**Alternatives considered**:

- Dependência em análise estática avançada ou serviço externo: descartada por complexidade desnecessária.
- Heurísticas exclusivamente textuais em documentação: descartadas por não capturar o comportamento real do código.
